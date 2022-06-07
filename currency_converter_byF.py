"""

A Currency Converter

"""

#import module
import sys
import datetime     #for providing date & time
from urllib.request import urlopen  #Python3はこの形式 for providing URL
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class Form(QDialog):
    def __init__(self, parent=None):
        #親クラス
        super(Form, self).__init__(parent)
        
        #UIアイテム
        self.fromComboBox = QComboBox()         #換算元通貨のリスト
        self.fromSpinBox = QDoubleSpinBox()     #換算する金額
        self.toComboBox = QComboBox()           #換算先通貨のリスト
        self.searchDate = QLineEdit(str(datetime.datetime.now().date()))    #レートを参照する日付

        #コンボボックスの幅と高さ
        self.fromComboBox.resize(400, 20)
        self.fromComboBox.setMinimumContentsLength(60)
        self.toComboBox.resize(400, 20)

        #コンボボックスのリスト項目設定
        date = self.getdata()   #データをhttpから読み込み
        rates = sorted(self.rates.keys()) #dictionaryをソートするとlistになる

        #ラベルの設定
        self.dateLabel = QLabel()
        self.dateLabel.setText(date)
        self.dateLabel.resize(400, 20)
        
        #コンボボックス他、アイテムの詳細設定
        self.fromComboBox.addItems(rates)   #QComboBoxはlistを受け取る
        self.fromSpinBox.setRange(0.01, 10000000.00)
        self.fromSpinBox.setValue(1.00)
        self.fromSpinBox.setSingleStep(0.1) #0.1単位での変更
        self.toComboBox.addItems(rates)
        self.toLabel = QLabel("1.00")
        self.quitButton = QPushButton("終了")
        self.quitButton.setFocusPolicy(Qt.NoFocus)  #enterで自動的に移動しない様にする

        #グリッドレイアウト　アイテムの配置　※（アイテム,行,列）
        grid = QGridLayout()
        grid.addWidget(self.dateLabel, 0, 0)
        grid.addWidget(self.searchDate, 0, 1)
        grid.addWidget(self.fromComboBox, 1, 0)
        grid.addWidget(self.fromSpinBox, 1, 1)
        grid.addWidget(self.toComboBox, 2, 0)
        grid.addWidget(self.toLabel, 2, 1)
        grid.addWidget(self.quitButton,3,2)

        #配置実行
        self.setLayout(grid)
        
        #signalの処理
        self.fromComboBox.currentIndexChanged.connect(self.updateUi)
        self.toComboBox.currentIndexChanged.connect(self.updateUi)
        self.fromSpinBox.valueChanged.connect(self.updateUi)
        self.searchDate.editingFinished.connect(self.searchdate_changed)
        self.quitButton.clicked.connect(qApp.quit)
        self.setWindowTitle("Currency")

    def set_comboBox_size(self,rates):
        if rates != []: #ratesが空でなければ下のを処理する
            self.fromComboBox.resize(400,20)
            self.toComboBox.resize(400, 20)


    #Signal動作
    def searchdate_changed(self):
        date = self.getdata()  # データをhttpから読み込み
        self.dateLabel.setText(date)        #いつのレートを出力したかを表示するラベル
        rates = sorted(self.rates.keys())  # dictionaryをソートするとlistになる
        self.fromComboBox.currentIndexChanged.disconnect(self.updateUi)  # コンボボックスをクリアするときに発生するシグナルを抑制する
        self.fromComboBox.clear()       #コンボボックスの項目の初期値設定
        self.fromComboBox.addItems(rates) # データの再設定
        self.fromComboBox.currentIndexChanged.connect(self.updateUi)
        self.toComboBox.currentIndexChanged.disconnect(self.updateUi)  # コンボボックスをクリアするときに発生するシグナルを抑制する
        self.toComboBox.clear()
        self.toComboBox.addItems(rates)  # データの再設定
        self.toComboBox.currentIndexChanged.connect(self.updateUi)
        self.set_comboBox_size(rates)

    def updateUi(self):
        to = self.toComboBox.currentText()
        from_ = self.fromComboBox.currentText()
        if self.rates[to] != 0:
            amount = (self.rates[from_] / self.rates[to]) * self.fromSpinBox.value()
        self.toLabel.setText("%0.2f" % amount)

    def getdata(self): # Idea was taken from the Python Cookbook
        self.rates = {} #辞書型
        series = 0
        self.description = []
        try:
            date = "Unknown"
            url_string = "https://www.bankofcanada.ca/valet/observations/group/FX_RATES_DAILY/csv?start_date="
            url_string = url_string + str(self.searchDate.text())       #URL末尾に取得年月日を付ける
            fh = urlopen(url_string)
            for line in fh:             #1行ずつURLのCSVデータを読んでいく
                line = line.decode()    #読み込んだデータはbyte型なのでstringに変換する
                #0：為替標記ラベルまで読み飛ばし
                if series == 0: #為替対象説明までの読み飛ばし作業
                    if not line.startswith('"id","label","description"\n'): 
                        continue #読み飛ばし
                    if series == 0:
                        series = 1
                        continue #為替対象標記も読み飛ばし
                elif series == 1: #為替対象説明をリストに記録する
                    if not line.startswith(("\n")):
                        fields = line.split(",")
                        append_string = (fields[2].strip("\n")).strip('"')
                        self.description.append(append_string)  # 為替対象説明をリストに登録(これは最終的にディクショナリのキーにsする）
                    else:
                        series = 2
                        continue
                elif series == 2: #為替レートのところまで読み飛ばし
                    if not line.startswith('"OBSERVATIONS"\n'):
                        continue
                    else:
                        series = 3
                        continue
                elif series == 3: #為替レート対象日の抽出
                    fields = line.split(",")
                    if not fields[0].startswith('"date"'):
                        continue
                    else:
                        series = 4
                        continue
                elif series == 4: #為替レート(値)を為替対象説明(キー)と共にディクショナリにして記録
                    series = 5
                    fields = (line.split(","))
                    i=0
                    for element in fields:
                        #print(str(i)+"回目")
                        if i==0:
                            date = fields[i]  # 0フィールド目はdate
                        else: #　１フィールド以降は為替レート
                            # dictionary へ登録
                            print(element)
                            if element != '""':
                                self.rates[self.description[i-1]] = float((((element.strip("\\")).strip("\"")).strip("\n")).strip("\""))
                            else:
                                self.rates[self.description[i-1]] = 0 #為替ﾃﾞｰﾀがない時がある。その時は0にする。
                        i = i + 1
            return "Exchange Rates Date: " + date.strip("\"")
        except Exception as e:
            return "Failed to download:\n%s" % e

if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = Form()
    form.show()
    sys.exit(app.exec_())
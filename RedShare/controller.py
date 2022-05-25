from PyQt5 import QtWidgets, QtGui, QtCore
from UI_RedShare_v2 import Ui_MainWindow
from PyQt5 import QtWidgets
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QFileDialog
import cv2
import time
import re


class MainWindow_controller(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow_controller, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setup_control()

    def setup_control(self):
        # --- setup GUI title ---
        self.setWindowTitle("Red-Share")
        # --- setupButton_openFile ---
        self.ui.pushButton_openFile.clicked.connect(self.openFile)
        # --- get article ---
        # self.ui.pushButton_return.clicked.connect(self.getArticle)
        self.ui.pushButton_return.clicked.connect(self.getNumber)

    # 開啟/抓取使用者選擇的json file
    def openFile(self):
        fileNames, fileTypes = QFileDialog.getOpenFileNames(self,
                                                            "open file",
                                                            "./")  # start file
        # --- 字體大小設定 ---
        font = QtGui.QFont()
        font.setPointSize(12)
        self.ui.textEdit_output.setFont(font)

        # --- 定義regex ---
        comp = re.compile('[0-9][0-9].json')
        fileList = []

        try:
            for i in fileNames:
                re_obj = comp.match(i[-7:])
                if re_obj:
                    print(f'符合\n{i}')
                    fileList.append(i)
                else:
                    print(f'不符合\n{i}')
                    self.ui.textEdit_output.setText(f'僅限開啟 \'json\' file')

            for i in fileList:
                print(f'抓取到的正確json:\n{i}')
            self.ui.textEdit_output.setText(f'Open Json File： {fileList[0][-7:]} ~ {fileList[-1][-7:]}')


        except:
            print(fileNames, '\nGUI讀取file name 失敗, 僅在程式中控台中顯示')
            self.ui.textEdit_output.setText('請打開"json"檔案')

        # --- 回傳正確的json ---
        return fileList

    # 抓取使用者輸入的文案
    def getArticle(self):
        # --- 定義抓取的article ---
        msg = self.ui.textEdit_article.toPlainText()
        # --- 字體大小設定 ---
        font = QtGui.QFont()
        font.setPointSize(12)
        self.ui.textEdit_output.setFont(font)
        # --- output get article ---
        if msg != '':
            self.ui.textEdit_output.setText(f'\t\t     文案讀取成功')
        else:
            self.ui.textEdit_output.setText(f'\t\t請輸入文案')
        return msg

    # 抓取使用者輸入的秒數
    def getSeconds(self):
        # --- 定義抓取的seconds ---
        second = self.ui.lineEditSeconds_1.text()  # 每則訊息間隔秒數
        second_2 = self.ui.lineEditSeconds_2.text()   # 冷卻時間秒數
        # --- 字體大小設定 ---
        font = QtGui.QFont()
        font.setPointSize(12)
        self.ui.textEdit_output.setFont(font)

        if second and second_2 != '':
            self.ui.textEdit_output.setText(f'\t\t     秒數讀取成功')
        else:
            self.ui.textEdit_output.setText(f'\t\t請輸入秒數設定')

        return second, second_2

    # 抓取使用者讀取的top level comments 編號
    def getNumber(self):
        # --- 定義抓取的number ---
        start_number = self.ui.lineEditCode_1.text()  # 要回覆的top level comment起始編號.
        end_number = self.ui.lineEditCode_2.text()  # 要回覆的top level comments 結尾編號.
        # --- 字體大小設定 ---
        font = QtGui.QFont()
        font.setPointSize(12)
        self.ui.textEdit_output.setFont(font)

        if start_number and end_number != '':
            self.ui.textEdit_output.setText(f'\t\t     編號讀取成功')
        else:
            self.ui.textEdit_output.setText(f'\t\t請輸入編號設定')

        return start_number, end_number

    # setup 進度條
    def setupProgressBar(self):
        pass


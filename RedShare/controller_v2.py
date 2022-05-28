from PyQt5 import QtWidgets, QtGui, QtCore
from UI_RedShare_v2 import Ui_MainWindow
from PyQt5.QtWidgets import QFileDialog
import time
import re

from datetime import datetime
import pymysql
import mysql.connector
import os
import googleapiclient.discovery
import googleapiclient.errors
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

# 測試規則：
# 1個帳號50秒回覆50則留言
# 冷卻時間120分鐘(7200秒)
# 一天約撒600則留言
# 一台電腦最多八開=一天4800留言
# 一週33600，抓1%，=336
# 現有24個帳號，336*3=一週一千

# 測試需求：
# 帳號* 8 , 預計每帳號留言600則回覆,
# 每200則回覆消耗1個oauth file, 一個帳號一天需要 3 個oauth file
# 秒數設定(訊息間隔/冷卻秒數), 1 / 7200秒
# oauth file, 每個帳號開啟3個oauth file
# 編號設定(起始/結束) x - x+600


class MainWindow_controller(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow_controller, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setup_control()
        self.fileList = []  # 用以收集user use oauth file.

    def setup_control(self):
        # --- setup GUI title ---
        self.setWindowTitle("Red-Share")
        # --- setupButton_openFile ---
        self.ui.pushButton_openFile.clicked.connect(self.openOauthFile)
        # --- setup pushButton_oauth, 驗證oauth file ---
        self.ui.pushButton_oauth.clicked.connect(self.oauth)
        # --- get article ---
        # self.ui.pushButton_return.clicked.connect(self.getArticle)  # 測試抓取文案
        # self.ui.pushButton_return.clicked.connect(self.getNumber)  # 測試抓取編號
        # self.ui.pushButton_return.clicked.connect(self.setupProgressBar)  # 測試進度條
        # --- setup 進度條 ---
        self.ui.progressBar.setValue(0)
        # --- execute program, connect "return button" ---
        self.ui.pushButton_return.clicked.connect(self.executeLoading)

    # 開啟/抓取使用者選擇的json file
    def openOauthFile(self):
        fileNames, fileTypes = QFileDialog.getOpenFileNames(self,
                                                            "open file",
                                                            "./")  # start file
        # --- 字體大小設定 ---
        font = QtGui.QFont()
        font.setPointSize(12)
        self.ui.textEdit_output.setFont(font)

        # --- use regex 規定json file 格式 ---
        comp = re.compile('[0-9][0-9].json')  # file name: "01.json"

        try:
            # 判斷開啟檔案是否為'.json', 若是, 加入list return 程式
            for i in fileNames:
                re_obj = comp.match(i[-7:])
                if re_obj:
                    # print(f'符合\n{i}')
                    self.fileList.append(i)
                else:
                    # print(f'不符合\n{i}')
                    self.ui.textEdit_output.setText(f'\n僅限開啟 \'json\' file')

            self.ui.textEdit_output.setText(f'Open Json File： {self.fileList[0][-7:]} ~ {self.fileList[-1][-7:]}')
            print(f'Open Json File： {self.fileList[0][-7:]} ~ {self.fileList[-1][-7:]}')
        except:
            print(fileNames, '\nGUI讀取file name 失敗, 僅在程式中控台中顯示')
            self.ui.textEdit_output.setText('\n請打開"json"檔案')

    def oauth(self):
        youtubeBot = insert_comments()
        if not self.fileList:
            self.ui.textEdit_output.setText('\n 請先開啟oauth file')
        else:
            self.ui.textEdit_output.setText('\n請依照 google 驗證您要回覆留言的帳號\n進行 Oauth 驗證初始化作業...')
            try:
                youtubeBot.OauthGoogleApi(Path_FileNames=self.fileList)
                self.ui.textEdit_output.setText('\ntoken 生成成功\nThe authentication flow has completed. 身分驗證流程已完成.')
            except UnicodeDecodeError as error:
                print(f'\nUnicodeDecode Error: {error}\n驗證失敗 ! 開啟檔案格式錯誤, 請開啟json file 進行驗證\n')
                self.ui.textEdit_output.setText('\nUnicodeDecode Error: {error}\n驗證失敗 ! 開啟檔案格式錯誤, 請開啟正確Oauth檔案\n')
            except:
                print('程式執行異常, 請與工程師反映您方才的操作與結果.\nERROR：Oauth File Error')
                self.ui.textEdit_output.setText('程式執行異常, 請與工程師反映您方才的操作與結果.\nERROR：Oauth File Error')

    def 判斷式(self):
        try:
            print('try 判斷式')
            startNumber = self.ui.lineEditCode_1.text()  # 要回覆的top level comment起始編號.
            endNumber = self.ui.lineEditCode_2.text()  # 要回覆的top level comments 結尾編號.

            sleep = []  # 建立冷卻區間.
            change = []  # 建立更換json file區間.
            totalNumber = int(endNumber) - int(startNumber)
            print(f'執行總數: {totalNumber}')
            i = 0  # sleep 區間.
            x = 0  # change 區間.
            while i != 86400:
                i += 50
                sleep.append(i)

            while x != 86400:
                x += 200
                change.append(x)

            # print(f'--- sleep ---\n第一位:{sleep[0]}\n第二位:{sleep[1]}\n第三位:{sleep[2]}\n最後位:{sleep[-1]}\n')
            # print(f'--- change ---\n第一位:{change[0]}\n第二位:{change[1]}\n第三位:{change[2]}\n最後位:{change[-1]}')

            self.ui.progressBar.setMaximum(totalNumber)  # setup 進度條
            y = 0  # json file 代號.
            for i in range(totalNumber):
                self.ui.progressBar.setValue(i)  # setup 進度條
                # print(f'i:{i}')
                print(f'總回覆數: {totalNumber}\n目前執行第: {i} 則留言')
                if i in sleep:
                    print(f'冷卻作業中, 預計冷卻{self.ui.lineEditSeconds_2.text()}秒')
                    self.ui.textEdit_output.setText(f'冷卻作業中, 預計冷卻{self.ui.lineEditSeconds_2.text()}秒')
                    time.sleep(self.ui.lineEditSeconds_2.text())
                    if i in change:
                        try:
                            y += 1
                            client_secrets_file = self.fileList[y]
                            print(f'目前使用oauth file:{client_secrets_file[-7:]}')
                            self.ui.textEdit_output.setText(f'目前使用oauth file: {client_secrets_file[-7:]}\n'
                                                            f'總回覆數: {totalNumber}')
                            return client_secrets_file
                        except:
                            # --- 若是json file 無法使用, 則使用下一個json file ---
                            y += 1
                            client_secrets_file = self.fileList[y]
                            print(f'上個json file無法使用, 目前使用:{client_secrets_file[-7:]}')
                            self.ui.textEdit_output.setText(f'上個json file無法使用, 目前使用:{client_secrets_file[-7:]}'
                                                            f'總回覆數: {totalNumber}')
                            return client_secrets_file
                else:
                    client_secrets_file = self.fileList[y]
                    print(f'目前使用oauth file:{client_secrets_file[-7:]}')
                    self.ui.textEdit_output.setText(f'目前使用oauth file: {client_secrets_file[-7:]}\n'
                                                    f'總回覆數: {totalNumber}')
                    return client_secrets_file
            print('判斷式 確認執行成功')

        except:
            print('開啟的Oauth File不足, 程式已經暫停執行, ')
            self.ui.textEdit_output.setText(f'開啟的Oauth File不足, 程式已經暫停執行, ')

    # main execute program function
    def executeLoading(self):
        # --- 定義user input ---
        article = self.ui.textEdit_article.toPlainText()               # offer 程式, 需要的文案.
        fileList = self.fileList                                       # offer 程式, 需要的oauth file.
        seconds_msgSleep = int(self.ui.lineEditSeconds_1.text())       # 每則訊息間隔秒數
        seconds_programSleep = int(self.ui.lineEditSeconds_2.text())   # 冷卻時間秒數
        startNumber = int(self.ui.lineEditCode_1.text())               # 要回覆的top level comment起始編號.
        endNumber = int(self.ui.lineEditCode_2.text())                 # 要回覆的top level comments 結尾編號.

        # --- 檢查user 輸入 ---
        if article == '':
            font = QtGui.QFont()
            font.setPointSize(12)
            self.ui.textEdit_output.setFont(font)
            self.ui.textEdit_output.setText('請輸入文案...')
        elif not fileList:
            self.ui.textEdit_output.setText('\n請開啟oauth file...')
        elif seconds_msgSleep == '':
            self.ui.textEdit_output.setText('\n請輸入秒數設定(訊息間隔)...')
        elif seconds_programSleep == '':
            self.ui.textEdit_output.setText('\n請輸入秒數設定(冷卻秒數)')
        elif seconds_msgSleep and seconds_programSleep == '':
            self.ui.textEdit_output.setText('\n請輸入秒數設定(訊息間隔/冷卻秒數)...')
        elif startNumber == '':
            self.ui.textEdit_output.setText('\n請輸入編號設定(起始)...')
        elif endNumber == '':
            self.ui.textEdit_output.setText('\n請輸入編號設定(結束)...')
        elif startNumber and endNumber == '':
            self.ui.textEdit_output.setText('\n請輸入編號設定(起始 / 結束)...')
        # --- 若通過程式上述檢查, execute the program ---
        else:
            self.ui.textEdit_output.setText('\n送出執行！')

            # --- 檢查 user input oauth file 是否符合需求 ---
            totalNumber = endNumber - startNumber
            needOauth = int(totalNumber / 200)
            oauthFile = len(fileList)

            # 若oauth file 需求數量計算為type(float), 則+1輸出為int()
            if type(needOauth) == float:
                needOauth = int(needOauth) + 1
            else:
                pass
            # 判斷開啟的oauth file 數量是否符合
            if oauthFile < needOauth:
                self.ui.textEdit_output.setText(f'還需要 {needOauth - oauthFile} 個oauth file執行程式\n'
                                                f'目前僅開啟 {len(fileList)} 個')
                print(f'還需要{needOauth - oauthFile}個oauth file, 執行程式, 目前僅開啟{len(fileList)}個')
                print(len(fileList))
            # --- user use oauthFile 充足, execute program ---
            else:
                self.ui.textEdit_output.setText(f'數量充足')
                print('oauth file 數量充足')

                # --- 送出執行 ---
                youtubeBot = insert_comments()
                self.oauth()

                try:
                    # --- executeFunction, readDatabase ---
                    youtubeBot.ReadSql_videoTopLevelComments_id(number1=startNumber, number2=endNumber)
                    print('資料庫讀取 成功')

                    # --- executeFunction, 判斷式 ---
                    # client_secrets_files 為呼叫 youtube data api v3需要使用的東東,
                    # 根據需求狀況, 需要控制多個Oauth file, 故撰寫成判斷式function,讓程式自主判斷各流程使用的 client_secrets_file與設定每則訊息間隔秒數
                    client_secrets_files = self.判斷式()
                    print('判斷式執行 成功')

                    # Read id data through db according to the function 逐一進行 insert top level comments
                    # # youtube_spider.data from youtube_spider.ReadSql_videoTopLevelComments_id() read data
                    print(f'youtube_spider.data:{youtubeBot.data}')
                    for i in youtubeBot.data:
                        video_name = i[0]
                        video_id = i[1]
                        comment_ids = i[3]
                        author_display_name = i[4]
                        top_level_comments = i[5]

                        # insert top level comments
                        print(f'client_secrets_files:\n{client_secrets_files}')
                        print(f'article:\n{article}')
                        insert_info = youtubeBot.insertTopLevelComments(client_secrets_file=client_secrets_files,
                                                                        reply_article=article,
                                                                        top_level_comment_id=comment_ids)
                        print('insert_info 成功')

                        # output insert top level comments 執行結果
                        # print(video_name, video_id, author_display_name)
                        # 初始化 sava data in DB, 整理並提取所需要的資料
                        youtubeBot.DataToDB_insert_comments(data=insert_info,
                                                            video_id=video_id,
                                                            video_name=video_name,
                                                            author_display_name=author_display_name,
                                                            top_level_comments=top_level_comments)
                        print('DataToDB_insert_comments 成功')

                        createData = youtubeBot.DataToDB_insert_comments(data=insert_info,
                                                                         video_id=video_id,
                                                                         video_name=video_name,
                                                                         author_display_name=author_display_name,
                                                                         top_level_comments=top_level_comments)

                        # 將整理好的 data 寫入資料庫
                        youtubeBot.save(createData, timeSleep=seconds_msgSleep)  # 設定for loop 休息秒數
                        print('save成功')

                except TypeError as error:
                    print(f'Error:\n{error}')
                    self.ui.textEdit_output.setText(f'Error:\n{error}')


# main class_insert top level comments
class insert_comments:
    def __init__(self):
        # 讀取資料庫使用
        self.data = []
        # 整理並提取需要資料使用
        self.list_VideoName = []
        self.list_VideoId = []
        self.list_CommendId = []
        self.list_AuthorDisplayName = []
        # 初始化_GoogleApiOauth()使用
        self.youtube = None

    def ReadSql_videoTopLevelComments_id(self, number1, number2):
        connection = mysql.connector.connect(host='127.0.0.1',
                                             port='3306',
                                             user='root',
                                             password='administrator',
                                             database='youtube',
                                             charset='utf8')
        cursor = connection.cursor()

        # 抓取MySQL table_video底下的top_level_comment_id
        cursor.execute(f'select * from top_level_comment where comment_number between {number1} and {number2};')  # 查詢第x筆~第y筆留言

        # 測試使用資料庫
        # cursor.execute(f'select * from top_level_comments_20220418 where comment_number between {number1} and {number2};')  # 查詢第100筆~第200筆留言

        records = cursor.fetchall()
        self.data = cursor.fetchall()

        # read DB_youtube > table_top_level_comment
        # create self.data, self.list_VideoName, self.list_VideoId, self.list_CommendId, self.list_AuthorDisplayName
        for r in records:
            self.data.append(r)
            self.list_VideoName.append(r[0])  # set video_name
            self.list_VideoId.append(r[1])  # set video_id
            self.list_CommendId.append(r[3])  # set commend_id
            self.list_AuthorDisplayName.append(r[4])  # set author_display_name

        # close command & 連線
        cursor.close()
        connection.commit()
        connection.close()

    def OauthGoogleApi(self, Path_FileNames):
        # 套件套件定義
        SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]
        print('\n登入 Oauth 驗證初始化作業...')
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

        try:
            # --- 驗證作業中 ---
            FileNames = Path_FileNames
            for i in FileNames:
                # print(i)  # print USE FileNames
                client_secrets_file = i

                creds = None

                # The file token.pickle stores the user's access and refresh tokens, and is
                # created automatically when the authorization flow completes for the first
                # 文件 token.pickle 存儲用戶的訪問和刷新令牌，並且是第一次授權流程完成時自動創建

                if os.path.exists(client_secrets_file + 'token.pickle'):
                    with open(client_secrets_file + 'token.pickle', 'rb') as token:
                        creds = pickle.load(token)
                # If there are no (valid) credentials available, let the user log in.
                # 如果沒有（有效）憑據可用，讓用戶登錄。
                if not creds or not creds.valid:
                    if creds and creds.expired and creds.refresh_token:
                        creds.refresh(Request())
                    else:
                        flow = InstalledAppFlow.from_client_secrets_file(
                            client_secrets_file, SCOPES)

                        creds = flow.run_local_server(port=0)

                    # Save the credentials for the next run
                    # 保存下一次運行的憑據
                    with open(client_secrets_file + 'token.pickle', 'wb') as token:
                        pickle.dump(creds, token)
                        print('\ntoken 生成成功')
                print(f'The authentication flow has completed. 身分驗證流程已完成.\n')

        except FileNotFoundError as error:
            print(f'\n{error}, 您輸入的帳號不存在, 請重新確認輸入!\n')

        except TypeError as error:
            print(f'\nERROR:{error}\n輸入不得為空, 請重新確認輸入\n')

    def insertTopLevelComments(self, client_secrets_file, reply_article, top_level_comment_id):
        # client_secrets_file is FUNCTION OauthGoogleApi & GUI class user select file,
        # it's google YouTube API 規矩下的產物，it's google account in gcp 開通 api key, oauth, 產生的 json.

        # 套件套件定義
        print('--- 自動化留言作業 ---')
        # os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

        try:
            creds = None  # account creds

            if os.path.exists(client_secrets_file + 'token.pickle'):
                with open(client_secrets_file + 'token.pickle', 'rb') as token:
                    creds = pickle.load(token)

            print('The authentication flow has completed. 身分驗證流程已完成.\n')

            youtube = googleapiclient.discovery.build(
                'youtube', 'v3', credentials=creds)

            request = youtube.comments().insert(
                part="snippet,id",
                body={
                    "snippet": {
                        "parentId": top_level_comment_id,  # Ugw26qI6J94wZ6m5he54AaABAg
                        "textOriginal": reply_article  # value by GUI Class get.
                    }
                }
            )
            response = request.execute()

            # print(f'response: {response}')
            # # response to list(data)
            # data = []
            # data.append(response)
            data = [response]
            return data

        except FileNotFoundError as error:
            print(f'\n{error}, 您輸入的帳號不存在, 請重新確認輸入!\n')

    def DataToDB_insert_comments(self, data, video_name, video_id, author_display_name, top_level_comments):
        # 以下整理並提取需要的資料
        comments = []  # 定義 comments 供給之後 to DB USE

        for data_item in data:
            data_item = data_item['snippet']

            try:
                # sample: 2020-08-03T16:00:56Z
                time_ = datetime.strptime(data_item['publishedAt'], '%Y-%m-%dT%H:%M:%SZ')
            except ValueError:
                # 日期格式錯誤
                time_ = None

            # # get insert_comment_google_account
            insert_comment_google_account = data_item.get('authorDisplayName', '')
            if not insert_comment_google_account:
                insert_comment_google_account = ''

            # # --- output 回覆過程 ---
            # MainWindow_controller.ui.textEdit_output.setText(f'影片:{video_name}'
            #                                                  f'作者:{author_display_name}'
            #                                                  f'留言:{top_level_comments}'
            #                                                  f'回覆帳號:{insert_comment_google_account}',
            #                                                  '回覆留言:', data_item['textOriginal'])

            # 撰寫 寫入db 的 reply_top_level_comment
            comments.append([
                video_name,
                video_id,
                data_item['parentId'],  # top_level_comment_ids
                author_display_name,  # (top_level_comment_authors)
                top_level_comments,  # top_level_comments
                insert_comment_google_account,  # insert_comment_google_account
                data_item['textOriginal'],  # reply_text
                time_  # reply time
            ])

        print('\n--- comments ---')
        print(f'影片:\n{comments[video_name]}\n'
              f'留言:{comments[top_level_comments]}\n'
              f'回覆:{comments[-2]}\n'
              f'回覆帳號:{comments[-3]}')

        return comments

    def save(self, comments, timeSleep):
        db_settings = {
            "host": "127.0.0.1",
            "port": 3306,
            "user": "root",
            "password": "administrator",
            "db": "youtube"
            # "charset": "utf8"
        }
        try:
            conn = pymysql.connect(**db_settings)

            with conn.cursor() as cursor:
                # --- 測試使用資料庫 ---
                # sql = """INSERT INTO insert_20220418(
                # --- 正式使用資料庫 ---
                sql = """INSERT INTO insert_top_level_comments(
                        video_name,
                        video_id,
                        top_level_comment_ids,
                        author_display_name,
                        top_level_comments,
                        insert_comment_google_account,
                        reply_text,
                        reply_time)
                     VALUES(%s, %s, %s, %s, %s, %s, %s, %s)"""

                for comment in comments:
                    cursor.execute(sql, comment)
                conn.commit()

        except Exception as ex:
            print("Exception:", ex)

        print(f'timeSleep: {timeSleep}')
        time.sleep(timeSleep)


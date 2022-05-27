
def re():
    import re
    string = 'Javaaascript'
    string2 = ['00.json', '01.json']

    # comp = re.compile('[Jj]ava')

    comp = re.compile('[0-9][0-9].json')
    for i in string2:
        print(i)
        re_obj = comp.match(i)
        if re_obj:
            print('正確')
        else:
            print('不正確')


def yoyo(totalNumber):
    import time
    # --- 冷卻區間 ---
    sleep = []
    # --- 更換json 區間 ---
    change = []
    fileList = []  # json file.
    # totalNumber = 9
    i = 0   # sleep 區間.
    x = 0   # change 區間.
    z = -1  # json file.

    while i != 86400:
        i += 50
        sleep.append(i)

    while x != 86400:
        x += 200
        change.append(x)

    while z != 200:
        z += 1
        fileList.append(z)

    # print(f'--- sleep ---\n第一位:{sleep[0]}\n第二位:{sleep[1]}\n第三位:{sleep[2]}\n最後位:{sleep[-1]}\n')
    # print(f'--- change ---\n第一位:{change[0]}\n第二位:{change[1]}\n第三位:{change[2]}\n最後位:{change[-1]}')

    y = 0  # json file 代號.
    print()
    for i in range(totalNumber):
        print(f'i:{i}')
        if i in sleep:
            print('休息2秒鐘')
            time.sleep(2)
            print('休息完成\n')
            if i in change:
                try:
                    y += 1
                    print(f'更換json file, 使用{fileList[y]}')
                    time.sleep(3)
                    print('更換完成')
                except:
                    y += 1
                    print(f'上個json file無法使用, 目前使用:{fileList[y]}')
                    time.sleep(3)
                    print('更換完成')
        else:
            print(f'fileList: {fileList[y]}')


def yoyoyo(oauthfile):
    startNumber = 1000
    endNumber = 1900
    totalNumber = endNumber - startNumber
    needOauth = totalNumber / 200

    # 若需要的oauth file 數量計算為float, 則+1輸出為整數
    if type(needOauth) == float:
        needOauth = int(needOauth) + 1
        print(f'start number: {startNumber}\n'
              f'end number: {endNumber}\n'
              f'total number: {totalNumber}\n'
              f'need oauth: {needOauth}')
    else:
        print(f'start number: {startNumber}\n'
              f'end number: {endNumber}\n'
              f'total number: {totalNumber}\n'
              f'need oauth: {needOauth}')

    # 判斷開啟的oauth file 數量是否符合
    if oauthfile < needOauth:
        print(f'還需要{needOauth - oauthfile}個oauth file')
    else:
        print('oauth file 數量充足')


if __name__ == '__main__':
    while True:
        yoyo(totalNumber=int(input('請輸入執行總數:')))



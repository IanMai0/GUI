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

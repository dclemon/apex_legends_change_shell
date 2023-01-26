import requests
from bs4 import BeautifulSoup
import json
import configparser
import time

def key_value_to_json(str):
    a = str.split('&')
    data_js = {}
    for b in a:
        c = b.split('=')
        data_js[c[0]] = c[1]
    return data_js
def getmidstring(html, start_str, end):
    start = html.find(start_str)
    if start >= 0:
        start += len(start_str)
        end = html.find(end, start)
        if end >= 0:
            return html[start:end].strip()


def write_ini(inikey, inivaluse, str, filepath):
    config = configparser.ConfigParser()

    config.read(filepath,encoding = 'utf-8')
    convaluse = config.set(inikey, inivaluse, str)
    config.write(open(filepath, "w"))
    return convaluse


def read_ini(inikey, inivaluse, filepath):
    config = configparser.RawConfigParser()

    config.read(filepath, encoding='utf-8')
    convaluse = config.get(inikey, inivaluse)
    return convaluse


def jd_checklogin(cokstr):
    print(cokstr)
    manual_cookies = {}
    for item in cokstr.split(';'):
        name, value = item.strip().split('=', 1)
        manual_cookies[name] = value
    cookie = manual_cookies
    print(cookie)
    b = str(gettime()[0])

    url = 'https://bean.jd.com/myJingBean/getListDetail?d=' + b
    print(url)
    head = {
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/75.0.3770.142 Safari/537.36',
        'ContentType': 'text/html; charset=utf-8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.8',
        'Connection': 'keep-alive',
        'Host': 'bean.jd.com',
        'Referer': 'https://bean.jd.com/myJingBean/list',
        'X-Requested-With': 'XMLHttpRequest',
        "sec-ch-ua": "\" Not A;Brand\";v=\"99\", \"Chromium\";v=\"99\", \"Google Chrome\";v=\"99\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        'Cookie': cokstr


    }

    res = requests.get(url, headers=head)
    c = json.loads(res.text)
    print(c)
    if c['code'] == '0000':
        d = True
    else:
        d = False
    print("是否登录：" + str(d))
    return d, cookie

def gettime():
    # 获取京东时间，延迟以及抢购时间
    url = 'https://api.m.jd.com/client.action?functionId=queryMaterialProducts&client=wh5'
    r = requests.get(url, timeout=5).json()
    jdtime = r["currentTime2"]
    localtime = int(time.time() * 1000)
    difftime = int(jdtime) - localtime
    return jdtime, difftime
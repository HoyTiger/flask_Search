import datetime
import os
import re

import jieba
import nltk
import requests
from bs4 import BeautifulSoup
from matplotlib import pyplot as plt


def get_proxy():
    return requests.get("http://127.0.0.1:5010/get/").json()


def delete_proxy(proxy):
    requests.get("http://127.0.0.1:5010/delete/?proxy={}".format(proxy))


def get_ip_port():
    if not os.path.exists('ip_port.txt'):
        return None
    with open('ip_port.txt', 'r', encoding='utf-8') as f:
        ip = f.readlines()
    return ip


def get_page(session, url, headers, proxies):
    try:
        real_url = get_real_url(url, headers)
        req = session.get(url, proxies=proxies)
        req.encoding = req.apparent_encoding
        return req, real_url
    except Exception as e:
        print('can not enter:', url, 'cause by:', e)
        return None, None


def get_real_url(v_url, headers):
    """
    获取百度链接真实地址
    :param v_url: 百度链接地址
    :return: 真实地址
    """
    r = requests.get(v_url, headers=headers, allow_redirects=False)  # 不允许重定向
    if r.status_code == 302:  # 如果返回302，就从响应头获取真实地址
        real_url = r.headers.get('Location')
    else:  # 否则从返回内容中用正则表达式提取出来真实地址
        real_url = re.findall("URL='(.*?)'", r.text)[0]
    print('real_url is:', real_url)
    return real_url


def clean(words):
    f = open('./static/stop_words.txt', 'r', encoding='utf-8')
    stop_words = []
    for line in f.readlines():
        stop_words.append(line.lower().strip())
    clean_words = []
    for word in words:
        if word.lower() not in stop_words:
            clean_words.append(word)
    return clean_words


def count_freq(html):
    soup = BeautifulSoup(html.content, "html.parser", from_encoding='gb18030')
    text = soup.get_text(strip=True)
    cop = re.compile("[^\u4e00-\u9fa5^a-z^A-Z^0-9]")  # 匹配不是中文、大小写、数字的其他字符
    text = cop.sub('', text)
    words = jieba.lcut(text)
    clean_words = clean(words)
    freq = nltk.FreqDist(clean_words)

    return freq


def IPList_61():
    ips = []
    for q in [1, 2]:
        url = 'http://www.66ip.cn/' + str(q) + '.html'
        html = requests.get(url)
        if html is not None:
            # print(html)
            iplist = BeautifulSoup(html.content, 'lxml')
            iplist = iplist.find_all('tr')
            i = 2
            for ip in iplist:
                if i <= 0:
                    loader = ''
                    # print(ip)
                    j = 0
                    for ipport in ip.find_all('td', limit=2):
                        if j == 0:
                            loader += ipport.text.strip() + ':'
                        else:
                            loader += ipport.text.strip()
                        j = j + 1
                    ips.append(loader)
                i = i - 1

    return ips

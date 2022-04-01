import configparser
import datetime
import os
import random
import re
import time
import matplotlib.pyplot as plt
from flask import jsonify

plt.rcParams['font.sans-serif'] = ['SimHei']  # 显示中文
plt.rcParams['axes.unicode_minus'] = False  # 显示负号

import nltk
import pandas as pd
import requests
from bs4 import BeautifulSoup
import jieba
from utils.config import *


def get_config():
    '''
    proxy 代理ip
    search 要搜索的内容
    page   搜索结果的前多少页
    num    每个搜索页面的结果
    sleep  休眠
    '''
    conf = {}
    config = configparser.ConfigParser()
    config.read("static/Config.ini", encoding='utf-8')
    conf['proxy'] = config['config']['proxy']
    conf['search'] = config['config']['search']
    conf['num'] = int(config['config']['num'])
    conf['page'] = int(config['config']['page'])
    conf['sleep'] = int(config['config']['sleep'])

    return conf


def google_search(q, page):
    ua = [
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36']

    df = pd.DataFrame(columns=['title', 'key_words', 'link'])
    freq = None
    filename = 'static/images/' + q + datetime.datetime.now().strftime('%Y_%m_%d_%H:%M:%S.%f') + '.png'
    url = "https://google.com.hk/search?btnG=Search&gbv=1?hl=zh-CN?lr=lang_zh-CN"
    for i in range(page):
        para = {
            'q': q,
            'num': 50,
            'start': i * 50
        }
        headers = {"user-agent": random.choice(ua)}

        try:
            resp = requests.get(url, para, headers=headers)
        except Exception as e:
            print(e)
            continue
        if resp.status_code == 200:
            results = []
            soup = BeautifulSoup(resp.content, "html.parser")
            for h in soup.find_all('h3'):
                anchors = h.find_parent('a')
                if anchors:
                    link = anchors['href']
                    title = h.text
                    item = {
                        "title": title,
                        "link": link
                    }
                    results.append(item)
            for item in results:
                print(item['link'])
                html = get_page(item['link'], headers)
                if html is None:
                    df = df.append({
                        'title': para['q'], 'key_words': '', 'link': ''
                    }, ignore_index=True)
                    continue
                else:
                    if freq is None:
                        freq = count_freq(html)
                    else:
                        freq.update(count_freq(html))
                    df = df.append({
                        'title': para['q'], 'link': item['link'], 'key_words': freq,
                    }, ignore_index=True)

        else:
            print('error')
    print('end')
    freq.plot(20, cumulative=False, show=False)
    plt.savefig(filename)
    plt.close()


def google_search2(q):
    ua = [
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36']

    url = "https://google.com.hk/search?btnG=Search&gbv=1?hl=zh-CN?lr=lang_zh-CN"

    para = {
        'q': q,
    }
    headers = {"user-agent": random.choice(ua)}

    try:
        resp = requests.get(url, para, headers=headers)
    except Exception as e:
        print(e)
        return '0'
    soup = BeautifulSoup(resp.content, "html.parser")
    for h in soup.find_all('nobr'):
        d = h.find_parent('div')
        if d:
            return d.text
        else:
            return '0'

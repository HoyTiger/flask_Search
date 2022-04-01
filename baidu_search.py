import configparser

import random
from fake_useragent import UserAgent

ua = UserAgent()
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['SimHei']  # 显示中文
plt.rcParams['axes.unicode_minus'] = False  # 显示负号
import pandas as pd

from utils.config import *

ip_list = open('baidu_ip.txt').readlines()

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


def baidu_search(q, page):
    session = requests.session()

    freq = None
    filename = 'static/images/' + q + datetime.datetime.now().strftime('%Y_%m_%d_%H:%M:%S.%f') + '.png'

    df = pd.DataFrame(columns=['title', 'key_words', 'link'])

    url = "https://www.baidu.com/s?usm=3&rsv_idx=2&rsv_page=1"
    for i in range(page):
        para = {
            'wd': q,
            'rn': 50,
            'pn': i * 50
        }
        headers = {"user-agent": ua.random,
                   "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                   "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
                   "Connection": "keep-alive",
                   "Accept-Encoding": "gzip, deflate, br",
                   'Cookie':'H_PS_PSSID=35836_36177_31254_34813_36167_34584_36140_36120_36193_36075_35994_26350_36046_36102_36061; PSINO=1; delPer=0; BD_CK_SAM=1; H_PS_645EC=8c6dttSAWaDXKzaujSaE3HOOQESUK0rhoeKXVZgurwuMuSGSZOOi0%2FsEZgbNWy5Wucf%2BQg; BDORZ=FFFB88E999055A3F8A630C64834BD6D0; BA_HECTOR=8ka0018kag8k210gbo1h4det90q; BD_UPN=143254; BDRCVFR[d9MwMhSWl4T]=mk3SLVN4HKm; BD_HOME=1; ab_sr=1.0.1_MmYyYzVlZTk5YThhYTY0Y2ExMzU3YmVhYzRlMTM0Mzk0Njg0YWI3MGZmODJlNzg3MDNjOGIwMWM5YThkODBjNDhjYzI3MTAwM2I2ZDNjNmY5YWI0YzI3MjE0NTE0Yzc5NjY3NzE5MTJiZjMyZjI2OWE1NmFhZjM4NDBlMzZkNzdjMGI5M2FlMDNjMDE0ZTA4MDdiMDJiNjc4ZGNlM2Y4ZQ==; MCITY=-144%3A131%3A; COOKIE_SESSION=52_0_5_6_26_14_1_0_5_4_0_2_63_0_24_0_1648802318_0_1648802294%7C9%232127476_35_1647839830%7C9; BIDUPSID=6A7115489E297FA3C628B29589C6BE56; __yjs_duid=1_082c81620f18aae9f89945fb2ba7cf6f1637554134098; BAIDUID=0520C9877171E63F53568A7E7983208A:FG=1; PSTM=1637554111'
                   }

        ip = random.choice(ip_list).strip()
        proxies = {"http": "http://" + ip}
        resp = session.get(url, params=para, headers=headers, proxies=proxies)

        if resp.status_code == 200:
            results = []
            soup = BeautifulSoup(resp.content, "html.parser")
            for h in soup.find_all('h3'):
                anchors = h.find_all('a')
                if anchors:
                    link = anchors[0]['href']
                    title = h.text
                    item = {
                        "title": title,
                        "link": link
                    }
                    results.append(item)

            for item in results:
                html, real_url = get_page(session, item['link'], headers, None)
                if html is None:
                    df = df.append({
                        'title': item['title'], 'link': real_url, 'key_words': '无法进入该网页'
                    }, ignore_index=True)
                    continue
                else:
                    if freq is None:
                        freq = count_freq(html)
                        df = df.append({
                            'title': item['title'], 'link': real_url, 'key_words': freq.keys(),
                        }, ignore_index=True)

                    else:
                        t = count_freq(html)
                        freq.update(t)
                        df = df.append({
                            'title': item['title'], 'link': item['link'], 'key_words': t.keys(),
                        }, ignore_index=True)



        else:
            print('error')

    print('end')
    # if freq is not None:
    freq.plot(20, cumulative=False, show=False)
    df.to_excel(filename.replace('images', 'files').replace('.png', '.xlsx'))
    plt.savefig(filename)
    plt.close()


def baidu_search2(q):
    ua = [
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36']

    url = "https://www.baidu.com/s"

    para = {
        'wd': q,
    }
    headers = {"user-agent": random.choice(ua)}

    try:
        resp = requests.get(url, para, headers=headers)
    except Exception as e:
        print(e)
        return '0'
    soup = BeautifulSoup(resp.content, "html.parser")
    for h in soup.find_all('span'):
        if '百度为您找到相关结果' in h.text:
            return h.text
    return '0'

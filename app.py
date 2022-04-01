from flask import Flask, request, render_template, Response, jsonify, send_from_directory
from utils.config import IPList_61


def baidu_ip_list():
    f = open('baidu_ip.txt', 'w')
    ip_list = IPList_61()
    for ip in ip_list:
        f.write(ip + '\n')
    f.close()


print('----获取百度代理池----')
baidu_ip_list()

from google_search import *
from baidu_search import *
import zipfile

app = Flask(__name__)
global a


@app.route('/')
def hello_world():  # put application's code here
    return render_template('index.html')


@app.route('/google_search', methods=["GET", "POST"])
def go_search():
    q = request.args.get("q")
    num = request.args.get("num", type=int)
    try:
        google_search(q, num // 50)
        return jsonify({'done': 1})
    except Exception as e:
        return jsonify({'done': 0, 'massage': str(e)})


@app.route('/baidu_search', methods=["GET", "POST"])
def bai_search():
    q = request.args.get("q")
    num = request.args.get("num", type=int)
    try:
        baidu_search(q, num // 50)
        return jsonify({'done': 1})
    except Exception as e:
        print(type(e))
        return jsonify({'done': 0, 'massage': str(e)})


@app.route('/show_spider')
def show_spider():
    type = request.args.get("type")
    keyword = request.args.get("kw")
    df = pd.DataFrame()
    try:
        if type == 'g':
            df = pd.read_csv("static/result_g/" + keyword + '.csv')
        elif type == 'b':
            df = pd.read_csv("static/result_b/" + keyword + '.csv')
        elif type == 'a':
            df = pd.read_csv("static/result_a/" + keyword + '.csv')
        df = df.rename(columns={'Unnamed: 0': 'ID'})

        return render_template('spider.html', html=df.to_html(index=False, classes=['layui-table-link', 'layui-table']),
                               type=type, keyword=keyword)
    except:
        return render_template('spider.html', html=df.to_html(index=False, classes=['layui-table-link', 'layui-table']),
                               type=type, keyword=keyword)


@app.route('/download')
def download():
    keyword = request.args.get("q")
    type = request.args.get("type")

    filelist = []
    print(type, keyword)
    df = pd.DataFrame()
    if type == 'g':
        filelist.append("static/result_g/" + keyword + '.csv')
        df = pd.read_csv("static/result_g/" + keyword + '.csv')
    elif type == 'b':
        filelist.append("static/result_b/" + keyword + '.csv')
        df = pd.read_csv("static/result_b/" + keyword + '.csv')
    elif type == 'a':
        filelist.append("static/result_a/" + keyword + '.csv')
        df = pd.read_csv("static/result_a/" + keyword + '.csv')

    for file in df['word_freq']:
        if os.path.exists(file):
            filelist.append(file)
    zf = zipfile.ZipFile(keyword + '.zip', 'w', zipfile.ZIP_DEFLATED)

    for tar in filelist:
        zf.write(tar, tar)

    return send_from_directory(r".", keyword + '.zip', as_attachment=True)


@app.route('/compare')
def compare():
    return render_template("compare.html")


@app.route('/to_compare')
def to_compare():
    kw1 = request.args.get("q")
    kw2 = request.args.get("q2")
    type = request.args.get("type")

    if type == 'g':
        q1 = google_search2(kw1)
        q2 = google_search2(kw2)
    else:
        q1 = baidu_search2(kw1)
        q2 = baidu_search2(kw2)
    return jsonify({'code': 1, 'q1': q1, 'q2': q2})


if __name__ == '__main__':
    app.run()

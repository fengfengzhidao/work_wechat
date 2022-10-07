# @Time:2022/10/6 22:27
# @Author:fengfeng
# 代码运行的主程序
from flask import Flask
from flask import render_template
from work_wechat_sdk.receives_message import ReceiveBaseWork
from work_wechat_sdk.web import we_hook

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@we_hook(app, '/hook/', work_name='default')
class RecvWork(ReceiveBaseWork):
    # 接收消息的回调
    def recv(self, user, msg):
        """
        :param user: 用户id
        :param msg: 消息内容
        :return:
        """
        print('default', user, msg)


@we_hook(app, '/morn/', work_name='morn')
class RecvWork(ReceiveBaseWork):
    # 接收消息的回调
    def recv(self, user, msg):
        """
        :param user: 用户id
        :param msg: 消息内容
        :return:
        """
        print('morn', user, msg)


if __name__ == '__main__':
    app.run(port=8005, debug=True)

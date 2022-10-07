# @Time:2022/10/6 22:27
# @Author:fengfeng
# 代码运行的主程序
from flask import Flask
from flask import request, render_template
from work_wechat_sdk.receives_message import ReceiveBaseWork, validation, user_message

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


# 自己编写一个类，继承ReceiveWork
class RecvWork(ReceiveBaseWork):
    # 接收消息的回调
    def recv(self, user, msg):
        """
        :param user: 用户id
        :param msg: 消息内容
        :return:
        """
        print('default', user, msg)


class RecvMornWork(ReceiveBaseWork):
    def recv(self, user, msg):
        """
        :param user: 用户id
        :param msg: 消息内容
        :return:
        """
        print('morn', user, msg)


@app.route('/hook/', methods=['GET', 'POST'])
def wechat_hook():
    # 实例化一个收消息的对象
    recv_work = RecvWork()

    if request.method == 'GET':
        return validation(recv_work)
    elif request.method == 'POST':
        return user_message(recv_work)


@app.route('/morn/', methods=['GET', 'POST'])
def wechat_morn_hook():
    # 实例化一个收消息的对象
    recv_work = RecvMornWork(work_name='morn')

    if request.method == 'GET':
        return validation(recv_work)
    elif request.method == 'POST':
        return user_message(recv_work)


if __name__ == '__main__':
    app.run(port=8005, debug=True)

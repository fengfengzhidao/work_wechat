# @Time:2022/10/6 22:27
# @Author:fengfeng
# 代码运行的主程序
from flask import Flask
from flask import render_template
from work_wechat_sdk import ReceiveBaseWork
from work_wechat_sdk import WorkMessage
from work_wechat_sdk.web import we_hook
from settings import CROPID, INSTALL_APP
import re

app = Flask(__name__)


@app.route('/')
def index():
    """用于展示一些可视化的数据"""

    def desensitization(val):
        # 将最中心的n/3个字符替换为*号
        # 6  12**23
        # 12 1234****1234
        # 21 1234567*******7654321
        # 5 12*22
        # 求总数
        all_count = len(val)
        div, mod = divmod(all_count, 3)
        return re.sub(r'(.{%s})(.*)(.{%s})' % (div, div), r'\1%s\3' % ('*' * (div + mod)), val)

    app_count = len(INSTALL_APP)

    data = {
        "app_count": app_count,
        "app_list": INSTALL_APP,
        "cropid": CROPID,
        "des": desensitization
    }

    return render_template('index.html', **data)


@we_hook(app, '/hook/', work_name='default')
class RecvWork(ReceiveBaseWork):

    def text(self, content):
        """
        :param content: 消息内容
        :return:
        """
        print('default', content, self.user)
        work = WorkMessage(to_user='fengfeng')
        work.send_text(content)

    def image(self, media_id, pic_url):
        print(media_id, pic_url)


@we_hook(app, '/morn/', work_name='morn')
class RecvWork(ReceiveBaseWork):
    # 接收消息的回调
    def text(self, content):
        """
        :param content: 消息内容
        :return:
        """
        print('morn', content, self.user)
        work = WorkMessage(work_name='morn', to_user='fengfeng')
        work.send_text(content)


if __name__ == '__main__':
    app.run(port=8005, debug=True)

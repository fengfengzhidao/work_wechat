# @Time:2022/10/6 22:50
# @Author:fengfeng
import requests
from settings import CROPID, INSTALL_APP
import json
import os

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36',
    'Content-Type': 'application/json'
}
base_url = 'https://qyapi.weixin.qq.com/cgi-bin/'


class BaseWork:
    def __init__(self, work_name='default', **kwargs):
        try:
            self.config = INSTALL_APP[work_name]
            self.access_token = AccessToken(self.config)
        except Exception:
            raise KeyError('the work_name does not exist！')


class AccessToken:
    """Token相关的处理类"""
    file_name = 'access_token.json'

    def __init__(self, config):
        # 判断是否有access_token这个文件
        self.Secret = config['Secret']
        self.access_token = ''
        if not os.path.exists(self.file_name):
            # 请求url获取access_token
            self.get_token()
            return
        # 如果存在，则取到其中的access_token
        self.load_token()

    def load_token(self):
        """
        读取token
        """
        with open(self.file_name, 'r')as f:
            json_str = json.load(f)
        self.access_token = json_str['access_token']
        return self.access_token

    def get_token(self):
        """获取token"""
        url = base_url + f'gettoken?corpid={CROPID}&corpsecret={self.Secret}'
        r = requests.get(url).json()
        self.access_token = r['access_token']
        # 创建文件，写入json
        self.save_token()
        return self.access_token

    def save_token(self):
        """将token保存到文件中"""
        with open(self.file_name, 'w')as f:
            json.dump({"access_token": self.access_token}, f)

    def __str__(self):
        return self.access_token


class WorkMessage(BaseWork):
    """推送消息的类"""
    payload = {}

    def __init__(self, work_name='default', **kwargs):
        super(WorkMessage, self).__init__(work_name, **kwargs)

        self.payload['touser'] = kwargs.get('to_user', '')  # 发给谁，用|连接
        self.payload['toparty'] = kwargs.get('to_party', '')  # 部门
        self.payload['totag'] = kwargs.get('to_tag', '')  # 标签
        self.payload['agentid'] = self.config["AgentId"]

    # 发送消息
    def __send_message(self):
        """发送消息的通用请求"""
        url = base_url + f"message/send?access_token={self.access_token}&random=69152"
        response = requests.request("POST", url, headers=headers, json=self.payload).json()
        code = response['errcode']
        if code == 42001:
            # token过期
            self.access_token = self.access_token.get_token()
            self.__send_message()
        print(response)

    # 发送具体的消息
    def send_text(self, content):
        """文本消息"""
        self.payload['msgtype'] = 'text'
        self.payload['text'] = {
            'content': content
        }
        self.__send_message()

    def send_markdown(self, content):
        """markdown消息"""
        self.payload['msgtype'] = 'markdown'
        self.payload['markdown'] = {
            'content': content
        }
        self.__send_message()

    def send_card(self, content):
        """卡片消息"""
        self.payload['msgtype'] = 'textcard'
        self.payload['textcard'] = content
        self.__send_message()

    def send_image(self, content):
        """图文消息"""
        self.payload['msgtype'] = 'news'
        self.payload['news'] = content
        self.__send_message()


class WorkMedia(BaseWork):
    """素材处理相关的类"""

    def get_media(self, media_id):
        res = requests.get(base_url + f"media/get?access_token={self.access_token}&media_id={media_id}").content
        return res


if __name__ == '__main__':
    """
    创建一个work实例，实例就是调用哪一个应用去发送消息
    """
    # access_token = AccessToken()
    # work = Work(work_name='morn', to_user='fengfeng')
    work = WorkMessage(to_user='fengfeng')
    # work.send_text('牛逼')
    """
    work.send_text('你好啊')
    """

    # 发送普通文本
    """
    work.send_text('你好')
    """

    # 发送markdown
    """
    work.send_markdown(
        '- 可发送markdown\n'
        '- 这是`高亮`的代码\n'
        '- 这是**加粗**的文本\n'
        '- 文字还可以有颜色\n'
        '1. <font color="info">开会</font>\n'
        '2. <font color="info">广州TIT 1楼 301</font>\n'
        '3. <font color="warning">2018年5月18日</font>\n'
        '4. <font color="comment">上午9:00-11:00</font>\n'
        '需要了解更多，请点击：[企业微信](https://work.weixin.qq.com)'
    )
    """

    # 发送卡片消息
    """
    work.send_card({
        "title": "早安",
        "description": f'<div class="gray">2022-10-07</div>'
                       '<div class="normal">总有一段难熬的日子,让你自我怀疑,不过当你经历多一点,你会发现,那只是生活的常态。</div>'
                       '<div class="highlight">加油，你是最美的</div>',
        "url": "http://www.fengfengzhidao.com",
        "btntxt": "原文链接"
    })
    """

    # 发送图文消息
    """
    work.send_image({
        "articles": [
            {
                "title": "中秋节礼品领取",
                "description": "今年中秋节公司有豪礼相送",
                "url": "http://www.fengfengzhidao.com",
                "picurl": "http://res.mail.qq.com/node/ww/wwopenmng/images/independent/doc/test_pic_msg1.png",
            },
            {
                "title": "端午节粽子领取",
                "description": "今年端午节公司有豪礼相送",
                "url": "http://www.fengfengzhidao.com",
                "picurl": "https://img2.baidu.com/it/u=1336564753,934091214&fm=253&fmt=auto&app=120&f=JPEG?w=700&h=400",
            }
        ]
    })
    """

    # 获取media文件
    # res = work.get_media('1E208uubo47RuCH9SdAMwTckAauuE8jn1f9mQgte3WqhQ-GgQZVjMqYfWY_t_eYlb')

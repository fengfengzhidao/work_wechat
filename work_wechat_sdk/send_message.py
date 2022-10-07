# @Time:2022/10/6 22:50
# @Author:fengfeng
import requests
from settings import CROPID, INSTALL_APP

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36',
    'Content-Type': 'application/json'
}
base_url = 'https://qyapi.weixin.qq.com/cgi-bin/'

payload = {

}


class Work:
    def __init__(self, work_name='default', **kwargs):
        """
        :param work_name:根据work_name去找对应的应用
        :param kwargs:
        """
        """
        conf:基本的配置信息
        """
        self.access_token = None
        try:
            self.config = INSTALL_APP[work_name]
        except Exception:
            raise KeyError('the work_name does not exist！')
        payload['touser'] = kwargs.get('to_user', '')  # 发给谁，用|连接
        payload['toparty'] = kwargs.get('to_party', '')  # 部门
        payload['totag'] = kwargs.get('to_tag', '')  # 标签
        payload['agentid'] = self.config["agentid"]

    def authentication(self):
        """鉴权"""
        url = base_url + f'gettoken?corpid={CROPID}&corpsecret={self.config["secretid"]}'
        r = requests.get(url).json()
        print(r)
        self.access_token = r['access_token']

    # 发送消息
    def __send_message(self):
        """发送消息的通用请求"""
        # 如果没有token
        if not self.access_token:
            self.authentication()
        url = base_url + f"message/send?access_token={self.access_token}&random=69152"
        response = requests.request("POST", url, headers=headers, json=payload).json()
        code = response['errcode']
        if code == 42001:
            # token过期
            self.authentication()
            self.__send_message()
        print(response)

    # 发送具体的消息
    def send_text(self, content):
        """文本消息"""
        payload['msgtype'] = 'text'
        payload['text'] = {
            'content': content
        }
        self.__send_message()

    def send_markdown(self, content):
        """markdown消息"""
        payload['msgtype'] = 'markdown'
        payload['markdown'] = {
            'content': content
        }
        self.__send_message()

    def send_card(self, content):
        """卡片消息"""
        payload['msgtype'] = 'textcard'
        payload['textcard'] = content
        self.__send_message()

    def send_image(self, content):
        """图文消息"""
        payload['msgtype'] = 'news'
        payload['news'] = content
        self.__send_message()


if __name__ == '__main__':
    """
    创建一个work实例，实例就是调用哪一个应用去发送消息
    """

    work = Work(work_name='morn', to_user='fengfeng')

    work.send_text('你好啊')
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

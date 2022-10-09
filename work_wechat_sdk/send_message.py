# @Time:2022/10/6 22:50
# @Author:fengfeng
import requests
from settings import CROPID, INSTALL_APP
import json
import os
from requests_toolbelt import MultipartEncoder
import re

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

    def upload_file(self, filename, filepath) -> str:
        """上传文件到素材库，返回media_id"""
        url = base_url + f'media/upload?access_token={self.access_token}&type=file'
        with open(filepath, 'rb') as f:
            m = MultipartEncoder(
                fields={'file': (filename, f, 'multipart/form-data')})

            response = requests.post(url=url, data=m, headers={
                'Content-Type': m.content_type}).json()
            if response['errmsg'] != 'ok':
                return ''
            return response['media_id']


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
            # 过期重新获取token，再次发送
            # token过期
            self.access_token = self.access_token.get_token()
            self.__send_message()
        print(response)

    def send_text(self, content, **kwargs):
        """
        其中content字段可以支持换行、以及a标签，即可打开自定义的网页
        :param content: 文本
        :param kwargs: 文本消息
        :return:
        """
        self.payload['msgtype'] = 'text'
        self.payload['text'] = {
            'content': content
        }
        # 表示是否是保密消息，0表示可对外分享，1表示不能分享且内容显示水印，默认为0
        self.payload['safe'] = kwargs.get('safe')
        # 表示是否开启id转译，0表示否，1表示是，默认0。仅第三方应用需要用到，企业自建应用可以忽略。
        self.payload['enable_id_trans'] = kwargs.get('enable_id_trans')
        # 表示是否开启重复消息检查，0表示否，1表示是，默认0
        self.payload['enable_duplicate_check'] = kwargs.get('enable_duplicate_check')
        # 表示是否重复消息检查的时间间隔，默认1800s，最大不超过4小时
        self.payload['duplicate_check_interval'] = kwargs.get('duplicate_check_interval')
        self.__send_message()

    def send_image(self, media_id, **kwargs):
        """图片消息"""
        self.payload['msgtype'] = 'image'
        self.payload['image'] = {
            "media_id": media_id
        }
        self.payload['safe'] = kwargs.get('safe')
        self.payload['enable_duplicate_check'] = kwargs.get('enable_duplicate_check')
        self.payload['duplicate_check_interval'] = kwargs.get('duplicate_check_interval')
        self.__send_message()

    def send_voice(self, media_id, **kwargs):
        """语音消息"""
        self.payload['msgtype'] = 'voice'
        self.payload['voice'] = {
            "media_id": media_id
        }
        self.payload['enable_duplicate_check'] = kwargs.get('enable_duplicate_check')
        self.payload['duplicate_check_interval'] = kwargs.get('duplicate_check_interval')
        self.__send_message()

    def send_video(self, media_id, title=None, description=None, **kwargs):
        """视频消息"""
        self.payload['msgtype'] = 'video'
        self.payload['video'] = {
            "media_id": media_id,
            "title": title,
            "description": description,
        }
        self.payload['safe'] = kwargs.get('safe')
        self.payload['enable_duplicate_check'] = kwargs.get('enable_duplicate_check')
        self.payload['duplicate_check_interval'] = kwargs.get('duplicate_check_interval')
        self.__send_message()

    def send_file(self, media_id, **kwargs):
        """文件消息"""
        self.payload['msgtype'] = 'file'
        self.payload['file'] = {
            "media_id": media_id
        }
        self.payload['safe'] = kwargs.get('safe')
        self.payload['enable_duplicate_check'] = kwargs.get('enable_duplicate_check')
        self.payload['duplicate_check_interval'] = kwargs.get('duplicate_check_interval')
        self.__send_message()

    def send_text_card(self, title, description, url, btntxt=None, **kwargs):
        """文本卡片消息"""
        self.payload['msgtype'] = 'textcard'
        self.payload['textcard'] = {
            "title": title,
            "description": description,
            "url": url,
            "btntxt": btntxt,
        }
        self.payload['enable_id_trans'] = kwargs.get('enable_id_trans')
        self.payload['enable_duplicate_check'] = kwargs.get('enable_duplicate_check')
        self.payload['duplicate_check_interval'] = kwargs.get('duplicate_check_interval')
        self.__send_message()

    def send_news(self, article_list: [dict], **kwargs):
        """图文消息，点击跳转网页"""
        """
        {
           "title" : "中秋节礼品领取",
           "description" : "今年中秋节公司有豪礼相送",
           "url" : "URL",
           "picurl" : "http://res.mail.qq.com/node/ww/wwopenmng/images/independent/doc/test_pic_msg1.png", 
           "appid": "wx123123123123123",
           "pagepath": "pages/index?userid=zhangsan&orderid=123123123",
        }
        """
        self.payload['msgtype'] = 'news'
        self.payload['news'] = {
            "articles": article_list,
        }
        self.payload['enable_id_trans'] = kwargs.get('enable_id_trans')
        self.payload['enable_duplicate_check'] = kwargs.get('enable_duplicate_check')
        self.payload['duplicate_check_interval'] = kwargs.get('duplicate_check_interval')
        self.__send_message()

    def send_mpnews(self, article_list: [dict], **kwargs):
        """新图文消息，点击进入详情页"""
        """
        {
           "title": "Title", 
           "thumb_media_id": "MEDIA_ID",
           "author": "Author",
           "content_source_url": "URL",
           "content": "Content",
           "digest": "Digest description"
        }
        """
        self.payload['msgtype'] = 'mpnews'
        self.payload['mpnews'] = {
            "articles": article_list,
        }
        self.payload['safe'] = kwargs.get('safe')
        self.payload['enable_id_trans'] = kwargs.get('enable_id_trans')
        self.payload['enable_duplicate_check'] = kwargs.get('enable_duplicate_check')
        self.payload['duplicate_check_interval'] = kwargs.get('duplicate_check_interval')
        self.__send_message()

    def send_markdown(self, content, **kwargs):
        """markdown消息"""
        self.payload['msgtype'] = 'markdown'
        self.payload['markdown'] = {
            'content': content
        }

        self.payload['enable_duplicate_check'] = kwargs.get('enable_duplicate_check')
        self.payload['duplicate_check_interval'] = kwargs.get('duplicate_check_interval')
        self.__send_message()

    def send_miniprogram_notice(self, app_id, page, title, content_item, **kwargs):
        """小程序通知消息"""
        self.payload['msgtype'] = 'miniprogram_notice'
        self.payload['miniprogram_notice'] = {
            "appid": app_id,
            "page": page,
            "title": title,
            "description": kwargs.get("description", None),
            "emphasis_first_item": kwargs.get("emphasis_first_item", True),  # 是否放大第一个content_item
            "content_item": content_item  # 消息内容键值对  {key: "", value:""}
        }

        self.payload['enable_id_trans'] = kwargs.get('enable_id_trans')
        self.payload['enable_duplicate_check'] = kwargs.get('enable_duplicate_check')
        self.payload['duplicate_check_interval'] = kwargs.get('duplicate_check_interval')
        self.__send_message()

    def send_template_card(self, **kwargs):
        """模板卡片消息"""
        self.payload['msgtype'] = 'template_card'
        self.payload['template_card'] = {
            "card_type": "text_notice",
        }
        self.payload['enable_id_trans'] = kwargs.get('enable_id_trans')
        self.payload['enable_duplicate_check'] = kwargs.get('enable_duplicate_check')
        self.payload['duplicate_check_interval'] = kwargs.get('duplicate_check_interval')
        return TemplateCard()


class TemplateCard(WorkMessage):

    def text_notice(self):
        """文本通知型"""
        self.payload['template_card']['card_type'] = "text_notice"

    def news_notice(self):
        """图文展示型"""
        self.payload['template_card']['card_type'] = "news_notice"

    def button_interaction(self):
        """按钮交互型"""
        self.payload['template_card']['card_type'] = "button_interaction"

    def vote_interaction(self):
        """投票选择型"""
        self.payload['template_card']['card_type'] = "vote_interaction"

    def multiple_interaction(self):
        """多项选择型"""
        self.payload['template_card']['card_type'] = "multiple_interaction"


class WorkMedia(BaseWork):
    """素材处理相关的类"""

    def get_media(self, media_id: str) -> (str, bytes):
        """
        :param media_id: 文件id
        :return: (文件名，文件字节流)
        """
        response = requests.get(base_url + f"media/get?access_token={self.access_token}&media_id={media_id}")
        header = response.headers
        if header.get('Error-Code'):
            self.access_token.get_token()
            self.get_media(media_id)
        else:
            pass

        file_name = re.findall(r'filename="(.*?)"', header['Content-disposition'])[0]
        return file_name, response.content


if __name__ == '__main__':
    pass

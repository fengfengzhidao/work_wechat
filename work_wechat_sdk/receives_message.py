# @Time:2022/10/7 10:57
# @Author:fengfeng
import time
from xml.dom.minidom import parseString

from flask import request

from settings import CROPID, INSTALL_APP
from work_wechat_sdk.wx_biz_msg_crypt import WXBizMsgCrypt


# 处理消息的类
class ReceiveBaseWork:
    """对数据进行处理，并分发到对应的方法中进行处理"""
    def __init__(self, work_name):
        """
        传入xml的数据，对其进行解析
        :param xml_string: xml的内容
        """
        try:
            self.config = INSTALL_APP[work_name]
        except Exception:
            raise KeyError('the work_name does not exist！')
        self._crypt = WXBizMsgCrypt(
            self.config["Token"],
            self.config["EncodingAESKey"],
            CROPID.encode()
        )

    def parse(self, xml_string):
        """解析xml"""
        doc = parseString(xml_string)
        self.xml_string = xml_string
        self._collection = doc.documentElement
        # 每个消息都有的内容
        self.to_user = self._get_by_tag_name("ToUserName")  # 企业微信CorpID
        self.user = self._get_by_tag_name("FromUserName")  # 成员UserID
        self.msg_type = self._get_by_tag_name("MsgType")  # 消息类型
        self.msg_id = self._get_by_tag_name("MsgId")  # 消息id，64位整型
        self.create_time = self._parse_time(self._get_by_tag_name("CreateTime"))  # 消息创建时间（整型） -> 转换为年月日 时分秒

        self.before()
        # 针对不同的消息类型，去执行不同的方法
        getattr(self, f"_{self.msg_type}")()
        self.after()

    def _get_by_tag_name(self, tag_name):
        return self._collection.getElementsByTagName(tag_name)[0].childNodes[0].data

    def _parse_time(self, time_stamp):
        time_array = time.localtime(int(time_stamp))  # 转化成对应的时间
        time_str = time.strftime("%Y-%m-%d %H:%M:%S", time_array)  # 字符串
        return time_str

    def _text(self):
        """文本消息"""
        content = self._get_by_tag_name('Content')
        self.text(content)

    def _image(self):
        """图片消息"""
        pic_url = self._get_by_tag_name('PicUrl')
        media_id = self._get_by_tag_name('MediaId')
        self.image(media_id, pic_url)

    def _voice(self):
        """语音消息"""
        format = self._get_by_tag_name('Format')  # 语音格式，如amr，speex等
        media_id = self._get_by_tag_name('MediaId')
        self.voice(media_id, format)

    def _link(self):
        """链接消息"""
        title = self._get_by_tag_name('Title')  # 标题
        description = self._get_by_tag_name('Description')  # 描述
        url = self._get_by_tag_name('Url')  # 链接跳转的url

        try:
            pic_url = self._get_by_tag_name('PicUrl')  # 封面缩略图的url
        except IndexError:
            pic_url = None

        self.link(title, description, url, pic_url)

    def _video(self):
        """视频消息"""
        thumb_media_id = self._get_by_tag_name('ThumbMediaId')  # 视频缩略图
        media_id = self._get_by_tag_name('MediaId')
        self.video(media_id, thumb_media_id)

    def _location(self):
        """定位消息"""
        location_x = self._get_by_tag_name('Location_X')  # 地理位置纬度
        location_y = self._get_by_tag_name('Location_Y')  # 地理位置经度
        scale = self._get_by_tag_name('Scale')  # 地图缩放大小
        label = self._get_by_tag_name('Label')  # 地理位置信息
        app_type = self._get_by_tag_name('AppType')  # app类型，在企业微信固定返回wxwork，在微信不返回该字段
        self.location(label, (location_x, location_y), scale, app_type)

    def before(self):
        """解析之前做的事情"""
        pass

    def text(self, content):
        print(content)

    def image(self, media_id, pic_url):
        print(media_id, pic_url)

    def voice(self, media_id, format):
        print(media_id, format)

    def link(self, title, desc, url, pic_url):
        print(title, desc, pic_url, url)

    def video(self, media_id, thumb_media_id):
        print(media_id, thumb_media_id)

    def location(self, label, location, scale, app_type):
        print(label, location)

    def after(self):
        """解析之后做的事情"""
        pass


# 添加的时候的验证
def validation(receive_work):
    msg_signature = request.args.get('msg_signature', '')
    timestamp = request.args.get('timestamp', '')
    nonce = request.args.get('nonce', '')
    echo_str = request.args.get('echostr', '')
    ret, res_str = receive_work._crypt.VerifyURL(msg_signature, timestamp, nonce, echo_str)
    if ret != 0:
        # 用户可能直接访问了这个接口
        print("ERR: VerifyURL ret: " + str(ret))
        return "failed"
    else:
        return res_str


# 用户发送消息来
def user_message(receive_work: ReceiveBaseWork):
    msg_signature = request.args.get('msg_signature', '')
    timestamp = request.args.get('timestamp', '')
    nonce = request.args.get('nonce', '')
    data = request.data.decode('utf-8')
    ret, msg_xml = receive_work._crypt.DecryptMsg(data, msg_signature, timestamp, nonce)

    if ret != 0:
        print("ERR: DecryptMsg ret: " + str(ret))
        return "failed"
    receive_work.parse(msg_xml)
    return "ok"

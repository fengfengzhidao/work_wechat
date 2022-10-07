# @Time:2022/10/7 10:57
# @Author:fengfeng
from xml.dom.minidom import parseString

from flask import request

from settings import CROPID, INSTALL_APP
from work_wechat_sdk.wx_biz_msg_crypt import WXBizMsgCrypt


class ReceiveBaseWork:
    def __init__(self, work_name='default', **kwargs):
        try:
            self.config = INSTALL_APP[work_name]
        except Exception:
            raise KeyError('the work_name does not exist！')
        self.crypt = WXBizMsgCrypt(
            self.config["Token"],
            self.config["EncodingAESKey"],
            CROPID.encode()
        )

    # 接收消息的回调
    def recv(self, user, msg):
        print('base recv：', user, msg)
        raise ValueError('改方法需要被重写')


# 添加的时候的验证
def validation(receive_work):
    msg_signature = request.args.get('msg_signature', '')
    timestamp = request.args.get('timestamp', '')
    nonce = request.args.get('nonce', '')
    echo_str = request.args.get('echostr', '')
    ret, res_str = receive_work.crypt.VerifyURL(msg_signature, timestamp, nonce, echo_str)
    if ret != 0:
        # 用户可能直接访问了这个接口
        print("ERR: VerifyURL ret: " + str(ret))
        return "failed"
    else:
        return res_str


# 用户发送消息来
def user_message(receive_work):
    msg_signature = request.args.get('msg_signature', '')
    timestamp = request.args.get('timestamp', '')
    nonce = request.args.get('nonce', '')
    data = request.data.decode('utf-8')
    ret, s_msg = receive_work.crypt.DecryptMsg(data, msg_signature, timestamp, nonce)

    if ret != 0:
        print("ERR: DecryptMsg ret: " + str(ret))
        return "failed"
    doc = parseString(s_msg)
    collection = doc.documentElement
    name_xml = collection.getElementsByTagName("FromUserName")
    msg_xml = collection.getElementsByTagName("Content")
    type_xml = collection.getElementsByTagName("MsgType")
    pic_xml = collection.getElementsByTagName("PicUrl")
    msg_type = type_xml[0].childNodes[0].data

    name = name_xml[0].childNodes[0].data  # 发送者id

    if msg_type == "text":  # 文本消息
        msg = msg_xml[0].childNodes[0].data  # 发送的消息内容
        receive_work.recv(name, msg)


    elif msg_type == "image":  # 图片消息
        pic_url = pic_xml[0].childNodes[0].data
        receive_work.recv(name, pic_url)

    return "ok"

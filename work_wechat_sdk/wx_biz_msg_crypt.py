import base64
import string
import random
import hashlib
import time
import struct
from Crypto.Cipher import AES
import xml.etree.ElementTree as ET
import socket
from work_wechat_sdk import ierror


class FormatException(Exception):
    pass


def throw_exception(message, exception_class=FormatException):
    raise exception_class(message)


class SHA1:

    @staticmethod
    def get_sha1(token, timestamp, nonce, encrypt):
        """
        用于SHA1算法生成安全签名
        :param token: 票据
        :param timestamp: 时间戳
        :param nonce: 随机字符串
        :param encrypt: 密文
        :return: 安全签名
        """
        try:
            sortlist = [token, timestamp, nonce, encrypt]
            sortlist.sort()
            sha = hashlib.sha1()
            sha.update(''.join(sortlist).encode())
            return ierror.WXBizMsgCrypt_OK, sha.hexdigest()
        except Exception as e:
            print(e)
            return ierror.WXBizMsgCrypt_ComputeSignature_Error, None


class XMLParse:
    """提供提取消息格式中的密文及生成回复消息格式的接口"""

    # xml消息模板
    AES_TEXT_RESPONSE_TEMPLATE = """
        <xml>
        <Encrypt><![CDATA[{resp[msg_encrypt]}]]></Encrypt>
        <MsgSignature><![CDATA[{resp[msg_signature]}]]></MsgSignature>
        <TimeStamp>{resp[timestamp]}</TimeStamp>
        <Nonce><![CDATA[{resp[nonce]}]]></Nonce>
        </xml>
    """

    def extract(self, xmltext):
        """
        提取出xml数据包中的加密消息
        :param xmltext: 待提取的xml字符串
        :return: 提取出的加密消息字符串
        """
        try:
            xml_tree = ET.fromstring(xmltext)
            encrypt = xml_tree.find('Encrypt')
            return ierror.WXBizMsgCrypt_OK, encrypt.text
        except Exception as e:
            print(e)
            return ierror.WXBizMsgCrypt_ParseXml_Error, None

    def generate(self, encrypt, signature, timestamp, nonce):
        """
        生成xml消息
        :param encrypt:加密后的消息密文
        :param signature: 安全签名
        :param timestamp: 时间戳
        :param nonce: 随机字符串
        :return: 生成的xml字符串
        """

        resp_dict = {
            'msg_encrypt': encrypt,
            'msg_signature': signature,
            'timestamp': timestamp,
            'nonce': nonce,
        }
        resp_xml = self.AES_TEXT_RESPONSE_TEMPLATE.format(resp=resp_dict)
        return resp_xml


class PKCS7Encoder:
    """
    提供基于PKCS7的加解密接口,AES加密前，数据需要采用PKCS#7填充至32字节的倍数
    """

    @staticmethod
    def encode(bytestring, block_size=32):
        """
        对需要加密的明文进行填充补位
        :param bytestring: 需要进行填充补位操作的明文
        :param block_size: 填充字节长度，默认32位
        :return: 补齐明文字符串
        """
        byte_length = len(bytestring)
        # 计算需要填空的位数
        val = block_size - (byte_length % block_size)
        # 获得补位所用的字符
        return bytestring + bytearray([val] * val)

    @staticmethod
    def decode(bytestring, block_size=32):
        """
        删除解密后明文的补位字符
        :param bytestring: 解密后的明文
        :param block_size: 填充字节长度，默认32位
        :return: 删除补位字符后的明文
        """
        val = bytestring[-1]
        if val > block_size:
            raise ValueError('Input is not padded or padding is corrupt')
        byte_length = len(bytestring) - val
        return bytestring[:byte_length]


class Prpcrypt:
    """提供接收和推送给企业微信消息的加解密接口"""

    def __init__(self, key):
        self.key = key  # AES算法的密钥，长度为32字节
        self.mode = AES.MODE_CBC  # 设置加解密模式为AES的CBC模式
        self.iv = key[:16]  # IV初始向量大小为16字节，取AESKey前16字节

    def encrypt(self, text, receiveid):
        """
        对明文进行加密
        :param text: 需要加密的明文
        :param receiveid:
        :return: 加密等到的字符串
        """
        # 16位随机字符串添加到明文开头，拼接明文字符串
        text = self.get_random_str() + struct.pack('!I', len(text)) + text.encode() + receiveid
        # 使用自定义的填充方式对明文进行补位填充
        text = PKCS7Encoder.encode(text)
        # 加密
        cryptor = AES.new(self.key, self.mode, self.iv)
        try:
            ciphertext = cryptor.encrypt(text)
            # 使用BASE64对加密后的字符串进行编码
            return ierror.WXBizMsgCrypt_OK, base64.b64encode(ciphertext)
        except Exception as e:
            print(e)
            return ierror.WXBizMsgCrypt_EncryptAES_Error, None

    def decrypt(self, text, receiveid):
        """
        对解密后的明文进行补位删除
        :param text: 密文
        :param receiveid:
        :return: 删除填充补位后的明文
        """
        try:
            cryptor = AES.new(self.key, self.mode, self.key[:16])
            # 使用BASE64对密文进行解码，然后AES-CBC解密
            plain_text = cryptor.decrypt(base64.b64decode(text))
        except Exception as e:
            print(e)
            return ierror.WXBizMsgCrypt_DecryptAES_Error, None
        try:
            val = plain_text[-1]
            content = plain_text[16:-val]
            xml_len = socket.ntohl(struct.unpack("I", content[: 4])[0])
            xml_content = content[4: xml_len + 4]
            from_receiveid = content[xml_len + 4:]
            # print('corpID:', from_receiveid)
        except Exception as e:
            print(e)
            return ierror.WXBizMsgCrypt_IllegalBuffer, None
        if from_receiveid != receiveid:
            return ierror.WXBizMsgCrypt_ValidateCorpid_Error, None
        return 0, xml_content

    def get_random_str(self):
        """
        随机生成16位字符串
        :return: 16位字符串
        """
        rule = string.ascii_letters + string.digits
        str = random.sample(rule, 16)
        return ''.join(str).encode()


class WXBizMsgCrypt:
    def __init__(self, token: str, EncodingAESKey: bytes, sReceiveId: bytes):
        """
        初始化加解密类
        :param token: str,接收消息服务器配置中填写的Token值
        :param EncodingAESKey: bytes,接收消息服务器配置中填写的EncodingAESKey，长度固定为43个字符
        :param sReceiveId: bytes,企业应用的回调，表示corpid,第三方事件的回调，表示suiteid
        """
        try:
            self.key = base64.b64decode(EncodingAESKey + b'=')
            # 用于AES加解密的key，长度为32字节
            assert len(self.key) == 32
        except:
            throw_exception('[error]: EncodingAESKey unvalid!', FormatException)
        self.m_sToken = token
        self.m_sReceiveId = sReceiveId

    def VerifyURL(self, sMsgSignature, sTimeStamp, sNonce, sEchoStr):
        ret, signature = SHA1.get_sha1(self.m_sToken, sTimeStamp, sNonce, sEchoStr)
        if ret:
            return ret, None
        if not signature == sMsgSignature:
            return ierror.WXBizMsgCrypt_ValidateSignature_Error, None
        pc = Prpcrypt(self.key)
        ret, sReplyEchoStr = pc.decrypt(sEchoStr, self.m_sReceiveId)
        return ret, sReplyEchoStr

    def EncryptMsg(self, sReplyMsg, sNonce, timestamp=None):
        """
        将企业回复用户的消息加密打包
        :param sReplyMsg: 企业号待回复用户的消息，xml格式的字符串
        :param timestamp: 时间戳，可以自己生成，也可以用URL参数的timestamp，如为None则自动用当前时间
        :param sNonce: 随机串，可以自己生成，也可以用URL参数的nonce
        :return: 成功0，sEncryptMsg，失败返回对应的错误码,None
        """
        pc = Prpcrypt(self.key)
        ret, encrypt = pc.encrypt(sReplyMsg, self.m_sReceiveId)
        if ret != 0:
            return ret, None
        if timestamp is None:
            timestamp = str(int(time.time()))
        # 生成安全签名
        encrypt = encrypt.decode()
        ret, signature = SHA1.get_sha1(self.m_sToken, timestamp, sNonce, encrypt)
        if ret != 0:
            return ret, None
        xml_parse = XMLParse()
        return ret, xml_parse.generate(encrypt, signature, timestamp, sNonce)

    def DecryptMsg(self, sPostData, sMsgSignature, sTimeStamp, sNonce):
        """
        检验消息的真实性，并且获取解密后的明文
        :param sPostData:密文，对应POST请求的数据
        :param sMsgSignature:签名串，对应URL参数的msg_signature
        :param sTimeStamp:时间戳，对应URL参数的timestamp
        :param sNonce:随机串，对应URL参数的nonce
        :return: 成功0，失败返回对应的错误码,xml_content: 解密后的原文
        """
        xmlParse = XMLParse()
        ret, encrypt = xmlParse.extract(sPostData)
        if ret != 0:
            return ret, None
        ret, signature = SHA1.get_sha1(self.m_sToken, sTimeStamp, sNonce, encrypt)
        if ret != 0:
            return ret, None
        if not signature == sMsgSignature:
            return ierror.WXBizMsgCrypt_ValidateSignature_Error, None
        pc = Prpcrypt(self.key)
        ret, xml_content = pc.decrypt(encrypt, self.m_sReceiveId)
        return ret, xml_content.decode()

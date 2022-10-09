# @Time:2022/10/5 10:17
# @Author:fengfeng

DEBUG = True

# 企业ID
CROPID = ''

# 应用配置列表，一个企业可以有多个应用
INSTALL_APP = {
    "default": {
        ####  发送消息配置  #####
        "label": "三方应用名",
        "Secret": '',  # 应用Secret
        "AgentId": 0,  # 应用id
        ####  接收消息配置  #####
        "URL": "",  # URL
        "Token": "",  # Token
        "EncodingAESKey": b"",  # EncodingAESKey
        # 这三个只要配置了就说明开启接收消息的功能了
    }
}

try:
    from local_settings import *
except ImportError:
    pass

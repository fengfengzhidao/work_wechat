# @Time:2022/10/7 15:11
# @Author:fengfeng
"""
web开发中，需要设置对应的url以及处理逻辑，大部分都是一样的，所以需要把相同代码抽离出来
"""
from flask import request
from work_wechat_sdk.receives_message import validation
from work_wechat_sdk.receives_message import user_message


def we_hook(app, url, work_name='default'):
    """
    flask模式下，快速使用本项目
    :param app: app
    :param url: 回调地址，一般是设置域名的path
    :param config: 如果有多app的情况，需要配置work_name参数
    :return:
    """

    def decorator(work_cls):

        def hook_fun():

            params = dict(request.args)

            if request.method == 'GET':
                # GET请求是首次添加的时候，需要进行服务器验证，以及用户直接在浏览器访问对应的url
                return validation(recv_work, params)
            elif request.method == 'POST':
                # POST请求就是对于用户在企业微信客户端发送的消息
                data = request.data.decode('utf-8')
                return user_message(recv_work, params, data)

        # 实例化发送消息的对象
        recv_work = work_cls(work_name)
        # 添加到路由，这里也可以用配置中的那个url，这样就可以少配置一点
        app.add_url_rule(url, url, hook_fun, methods=['GET', "POST"])
        return recv_work

    return decorator

# WorkWechat

博主所用python版本为3.9.8

web框架用的是`flask`

本项目为针对 **个人用户** 的企业微信api接口，实现方便的收发消息

针对初学者，跟着官方那个配置文档，可能有点不太方便，本项目可以方便的配置企业微信，做到开箱即用

[企业微信官方文档](https://developer.work.weixin.qq.com/document/path/90664)

先注册一个企业微信

# 创建应用

![](http://python.fengfengzhidao.com/pic/20221007142314.png)
![](http://python.fengfengzhidao.com/pic/20221007142609.png)
![](http://python.fengfengzhidao.com/pic/20221007142711.png)

# 发消息配置

如果是创建的第一个应用，是可以不用配置企业可信ip的

将应用中的AgentId和Secret填入settings中的INSTALL_APP对应的配置项中

例如

```python
# 应用配置列表，一个企业可以有多个应用
INSTALL_APP = {
    "default": {
        ####  发送消息配置  #####
        "label": "应用名",
        "secretid": '',  # 应用Secret
        "agentid": 1000003,  # 应用id
        ####  接收消息配置  #####
        "URL": "",  # URL
        "Token": "",  # Token
        "EncodingAESKey": "",  # EncodingAESKey
        # 这三个只要配置了就说明开启接收消息的功能了
    }
}
```

配置成功之后，可以运行这段代码进行测试

```python
from work_wechat_sdk import WorkMessage

work = WorkMessage(work_name='default', to_user='xxx')
# work_name 是调用对应的应用去实现
# to_user 发送给某个人
work.send_text('测试数据')
```

## 发消息API

需要实例化一个message对象

```python
from work_wechat_sdk import WorkMessage

work = WorkMessage(work_name='default', to_user='xxx')
```

参数详解

- work_name:对应使用的app
- to_user:发送给谁
- to_party:发送给哪个部门
- to_tag:发送给对应标签

### 文本消息

```python
from work_wechat_sdk import WorkMessage

work = WorkMessage(work_name='default', to_user='xxx')
work.send_text(content="文本内容")
```

### 图片消息

```python
from work_wechat_sdk import WorkMessage

work = WorkMessage(work_name='default', to_user='xxx')
work.send_image(media_id="xxx-xxx-xx")
```

### 语音消息

```python
from work_wechat_sdk import WorkMessage

work = WorkMessage(work_name='default', to_user='xxx')
work.send_voice(media_id="xxx-xxx")
```

### 视频消息

```python
from work_wechat_sdk import WorkMessage

work = WorkMessage(work_name='default', to_user='xxx')
work.send_video(media_id="xxx-xxx", title='视频标题', description='视频简介')
```

### 文件消息

```python
from work_wechat_sdk import WorkMessage

work = WorkMessage(work_name='default', to_user='xxx')
work.send_file(media_id="xxx-xxx")
```

### 文本卡片消息

```python
from work_wechat_sdk import WorkMessage

work = WorkMessage(work_name='default', to_user='xxx')
work.send_text_card(
    title='卡片标题',
    description='卡片简介',
    url='xxx',
    btntxt='更多'
)
```

### 图文消息

```python
from work_wechat_sdk import WorkMessage

work = WorkMessage(work_name='default', to_user='xxx')
work.send_news(article_list=[
    {
        "title": "中秋节礼品领取",
        "description": "今年中秋节公司有豪礼相送",
        "url": "URL",
        "picurl": "http://res.mail.qq.com/node/ww/wwopenmng/images/independent/doc/test_pic_msg1.png",
        "appid": "wx123123123123123",
        "pagepath": "pages/index?userid=zhangsan&orderid=123123123",
    }
])
```

### 新图文消息

```python
from work_wechat_sdk import WorkMessage

work = WorkMessage(work_name='default', to_user='xxx')
work.send_mpnews(article_list=[
    {
        "title": "Title",
        "thumb_media_id": "MEDIA_ID",
        "author": "Author",
        "content_source_url": "URL",
        "content": "Content",
        "digest": "Digest description"
    }
])
```

### markdown消息

```python
from work_wechat_sdk import WorkMessage

work = WorkMessage(work_name='default', to_user='xxx')
work.send_markdown(content="markdown内容")
```

### 小程序通知消息

```python
from work_wechat_sdk import WorkMessage

work = WorkMessage(work_name='default', to_user='xxx')
work.send_miniprogram_notice(
    app_id="xxx",
    page='page',
    title='标题',
    content_item=[
        {
            "key": "key",
            "value": "value"
        }
    ]
)
```

### 模板消息

# 接收消息配置

## 服务器配置

配置URL，Token，EncodingAESKey
![](http://python.fengfengzhidao.com/pic/20221007145527.png)

## 代码使用

```python
from flask import Flask
from work_wechat_sdk.receives_message import ReceiveBaseWork
from work_wechat_sdk.web import we_hook

app = Flask(__name__)


@we_hook(app, '/hook/', work_name='default')
class RecvWork(ReceiveBaseWork):
    # 接收消息的回调
    def text(self, content):
        """
        :param content: 消息内容
        :return:
        """
        print('default', self.user, content)

    def image(self, media_id, pic_url):
        """
        :param media_id: 素材id
        :param pic_url: 图片的预览链接
        :return:
        """

```

我们需要编写一个类，去继承ReceiveBaseWork，这个类中的text方法就代表接收text消息的回调

content则是消息内容

一共提供了六种方法，分别对应六种类型的回调

| 方法 | 介绍 | 参数 |
|---- | ---- |---- |
| text | 文本消息| content |
| image | 图片消息 | media_id pic_url |
| voice | 语音消息 | media_id format |
| link | 链接 | title desc url pic_url |
| video | 视频 | media_id thumb_media_id |
| location | 定位 | label location scale app_type |

参数类型详见 [消息格式](https://developer.work.weixin.qq.com/document/path/90857)

web_hook则是做类和视图挂载到路由的作用

它一共有三个参数

第一个是app

第二个是路由

第三个关键字参数是调用哪一个应用去接收，默认是default
import time
import xml.etree.ElementTree as ET
import hashlib
import threading
import requests

from noval.api import find_noval_by_name, find_noval_content
import uuid

from wechat.AccessTokenManager import AccessTokenManager

appid = 'wxab4dc66c109f29f3'  # 替换为你的appid
appsecret = '1d35e2a12f170eac4301b8b3f5037990'  # 替换为你的appsecret

content_cache = {}

def get_content_by_id(book):
    if book is None or book == '' or book not in content_cache:
        return '暂无数据'
    if book in content_cache:
        return content_cache[book]

def wechat_msg(request):
    if request.method == 'GET':
        # 处理微信服务器的验证请求
        token = 'magiccsq'  # 替换为你配置的 Token
        signature = request.args.get('signature', '')
        timestamp = request.args.get('timestamp', '')
        nonce = request.args.get('nonce', '')
        echostr = request.args.get('echostr', '')

        # 验证签名
        lst = [token, timestamp, nonce]
        lst.sort()
        sha1 = hashlib.sha1()
        sha1.update(''.join(lst).encode('utf-8'))
        hashcode = sha1.hexdigest()

        if hashcode == signature:
            return echostr
        else:
            return ''
    else:
        # 处理用户发送的消息
        data = request.get_data()
        print(data)
        xml_data = ET.fromstring(data)
        print('消息：' + xml_data)
        to_user = xml_data.find('ToUserName').text
        from_user = xml_data.find('FromUserName').text
        msg_type = xml_data.find('MsgType').text
        content = xml_data.find('Content').text
        msg_id = xml_data.find('MsgId').text
        reply_content = '''📚 欢迎使用灵犀机器人 📚
    我能帮您轻松查找您想阅读的书籍及其故事会内容。您只需按照以下格式发送消息，我就能为您提供所需信息：

    1️⃣ 查找故事会
    发送消息格式：书名#您想查询的书名
    例如：书名#哈利·波特

    2️⃣ 查找全文
    发送消息格式：故事会#您想查询的故事会标题
    例如：故事会#哈利·波特与魔法石

    快来试试吧！输入相应的命令，开启您的阅读之旅。如果您在使用过程中有任何疑问，随时向我发送消息，我随时准备帮助您。'''
        # 根据消息类型和内容进行相应的处理
        if msg_type == 'text':
            if content.startswith('书名#'):
                book_name = content[3:]
                reply_content = f'正在为您查找《{book_name}》的相关信息，请稍候片刻，我们将尽快为您呈现结果。'
                threading.Thread(target=find_book_sync, args=(book_name,from_user)).start()
            elif content.startswith('故事会#'):
                story_id = content[4:]
                reply_content = f'正在获取《{story_id}》的全文内容，请耐心等待，我们即将展示完整故事给您。'
                threading.Thread(target=find_content_sync, args=(story_id, from_user)).start()
                # reply_content = '点击链接查看全文：\n https://liuyf.zicp.io/content?book=' + book_id

        # 返回响应给微信服务器
        print(reply_content)
        response = generate_response(from_user, to_user, reply_content)
        return response



def generate_response(to_user, from_user, content):
    response_template = '''
        <xml>
          <ToUserName><![CDATA[{to_user}]]></ToUserName>
          <FromUserName><![CDATA[{from_user}]]></FromUserName>
          <CreateTime>{create_time}</CreateTime>
          <MsgType><![CDATA[text]]></MsgType>
          <Content><![CDATA[{content}]]></Content>
        </xml>
        '''

    response = response_template.format(
        to_user=to_user,
        from_user=from_user,
        create_time=int(time.time()),
        content=content
    )

    return response

def find_book_sync(book_name, user):
    book_list = find_noval_by_name(book_name)['data']
    res = '\n'.join(book_list)
    send_customer_service_message(user, res.encode().decode('unicode-escape'))

def find_content_sync(book_name, user):
    md5 = hashlib.md5()
    md5.update(book_name.encode('utf-8'))
    book_id = md5.hexdigest()
    content = find_noval_content(book_name)['concent']
    content_cache[book_id] = content
    res = '点击链接查看全文：\n https://liuyf.zicp.io/content?book=' + book_id
    send_customer_service_message(user, res.encode().decode('unicode-escape'))

def send_customer_service_message(user_openid, message):
    # 示例使用

    token_manager = AccessTokenManager(appid, appsecret)

    # 获取access_token
    access_token = token_manager.get_access_token()
    print(access_token)
    """
    使用客服消息异步回复用户

    :param access_token: 公众号的access_token
    :param user_openid: 用户的OpenID
    :param message: 要发送的消息内容
    """
    # 微信公众号发送客服消息的API URL
    url = f"https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token={access_token}"

    # 构造发送的消息数据
    data = {
        "touser": user_openid,
        "msgtype": "text",
        "text": {
            "content": message
        }
    }

    # 发送POST请求
    response = requests.post(url, json=data)

    # 检查请求是否成功
    if response.status_code == 200:
        result = response.json()
        if result.get("errcode") == 0:
            print("消息发送成功")
        else:
            print(f"消息发送失败，错误码：{result.get('errcode')}，错误信息：{result.get('errmsg')}")
    else:
        print(f"HTTP请求失败，状态码：{response.status_code}")
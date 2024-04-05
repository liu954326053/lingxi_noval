import requests
import time

class AccessTokenManager:
    def __init__(self, appid, appsecret):
        """
        初始化AccessToken管理器

        :param appid: 公众号的appid
        :param appsecret: 公众号的appsecret
        """
        self.appid = appid
        self.appsecret = appsecret
        self.access_token = None
        self.expires_at = 0

    def get_access_token(self):
        """
        获取有效的access_token，如果当前token过期则重新获取

        :return: 有效的access_token
        """
        current_time = time.time()
        if self.access_token is None or current_time >= self.expires_at:
            # 获取新的access_token
            url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={self.appid}&secret={self.appsecret}"
            response = requests.get(url)
            if response.status_code == 200:
                result = response.json()
                print(result)
                self.access_token = result.get("access_token")
                # 设置token过期时间
                self.expires_at = current_time + result.get("expires_in") - 300  # 提前5分钟过期
                print("新的access_token获取成功")
            else:
                print("获取access_token失败")
        return self.access_token



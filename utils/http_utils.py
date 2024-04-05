import requests

class HttpRequest:
    def __init__(self, base_url, default_headers=None):
        self.base_url = base_url
        self.session = requests.Session()
        self.default_headers = default_headers or {}

    def get(self, endpoint, params=None, headers=None):
        url = self.base_url + endpoint
        merged_headers = {**self.default_headers, **(headers or {})}
        try:
            response = self.session.get(url, params=params, headers=merged_headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"GET 请求错误: {e}")
            return None

    def post(self, endpoint, data=None, json=None, headers=None):
        url = self.base_url + endpoint
        merged_headers = {**self.default_headers, **(headers or {})}
        try:
            response = self.session.post(url, data=data, json=json, headers=merged_headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"POST 请求错误: {e}")
            return None

    def close(self):
        self.session.close()
import json

from utils.http_utils import HttpRequest

key = 'TK195B044A82B3A13D4B0D944B945F2F05'
book_cache = {}

def find_noval_by_name(name):
    base_url = "http://103.239.244.123:81/"
    default_headers = {
        "accept": "application/json, text/javascript, */*",
        "accept-language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        "content-type": "application/x-www-form-urlencoded",
        "x-requested-with": "XMLHttpRequest"
    }

    http = HttpRequest(base_url, default_headers)
    param = {'book_name': name}
    res = http.post("/php/search_file.php", param, {'Cookie': key})
    list = []
    for i in res['data'].split('丨'):
        print(i)
        if i is not None and i != '':
            list.append(i)
    return {'data': list}


def find_noval_content(book_name):
    base_url = "http://103.239.244.123:81/"
    default_headers = {
        "accept": "application/json, text/javascript, */*",
        "accept-language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        "content-type": "application/x-www-form-urlencoded",
        "x-requested-with": "XMLHttpRequest"
    }
    http = HttpRequest(base_url, default_headers)
    param = {'book_name': book_name, 'kami': key}
    res = http.post("php/search_file_info.php", param)
    book_data = json.loads(res['data'])
    book_data['concent'] = book_data['concent'].replace('<p>', '').replace('</p>', '\n').replace('<br><br>', '<br>').replace('<br>', '\n')
    return book_data

# book_list = find_noval_by_name('她的红白玫瑰')
# content = find_noval_content(book_list[0])
# print(content)

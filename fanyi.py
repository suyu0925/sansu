import random
import string
from hashlib import md5

import requests

import config

def translate(q: str, source: str = 'auto', to:str = 'en'):
    payload = {
        'q': q,
        'from': source,
        'to': to,
        'salt': ''.join(random.choice(string.ascii_letters + string.digits) for i in range(12)),
        'appid': config.fanyi_appid,
        'sign': '',
    }
    content = payload['appid'] + q + payload['salt'] + config.fanyi_key
    payload['sign'] = md5(content.encode('utf-8')).hexdigest()

    r = requests.get('https://fanyi-api.baidu.com/api/trans/vip/translate', params=payload)
    data = r.json()
    return data['trans_result'][0]['dst']

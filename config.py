import os
from dotenv import load_dotenv

load_dotenv()

port = os.environ['PORT']

# wechat mp
token = os.environ['TOKEN']
appid = os.environ['APP_ID']
appsecret = os.environ['APP_SECRET']

# tencent cloud for tts
tencentcloud_appid = os.environ['TENCENTCLOUD_SECRET_ID']
tencentcloud_appsecret = os.environ['TENCENTCLOUD_SECRET_KEY']

# stability for ai paint
stability_key = os.environ['STABILITY_KEY']

# fanyi for translate
fanyi_appid = os.environ['BAIDU_FANYI_APPID']
fanyi_key = os.environ['BAIDU_FANYI_KEY']

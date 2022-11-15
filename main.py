import base64
import os
import re
import uuid
from enum import Enum

import requests
import werobot
from tencentcloud.common import credential
from tencentcloud.tts.v20190823 import models, tts_client
from werobot.replies import ImageReply, VoiceReply

import config
import fanyi
import stability

robot = werobot.WeRoBot(token=config.token)
robot.config['APP_ID'] = config.appid
robot.config['APP_SECRET'] = config.appsecret
client = robot.client

cred = credential.Credential(
    config.tencentcloud_appid, config.tencentcloud_appsecret)
tencentcloud_client = tts_client.TtsClient(cred, "ap-shanghai")


class Stage(str, Enum):
    Idle = '待机'
    TTS = '语音合成'
    Chat = '闲聊'
    AIPaint = '智能画画'


Prompt = """\
请发送关键词以进入相应模式：
    闲聊
    语音合成
    智能画画
"""


@robot.handler
def hello(message):
    return 'Hello World!'


@robot.subscribe
def subscribe(message):
    return Prompt


@robot.unsubscribe
def unsubscribe(message, session):
    session['stage'] = Stage.Idle


@robot.filter("语音合成")
def enter_tts(message, session):
    if session['stage'] == Stage.Idle:
        session['stage'] = Stage.TTS
        return "进入*语音合成*模式，请直接发送要合成的文本。退出请发送/q"


def tts(text, message):
    req = models.TextToVoiceRequest()
    req.Text = f"""<speak>{text}</speak>"""
    req.VoiceType = 101016
    req.SessionId = str(uuid.uuid4())
    res = tencentcloud_client.TextToVoice(req)
    with open(f'./{req.SessionId}.mp3', 'wb') as f:
        f.write(base64.b64decode(res.Audio))
    with open(f'./{req.SessionId}.mp3', 'rb') as f:
        res = client.upload_media('voice', f)
    os.remove(f'./{req.SessionId}.mp3')
    return VoiceReply(
        message=message,
        media_id=res['media_id']
    )


@robot.filter('闲聊')
def entry_chat(message, session):
    if session['stage'] == Stage.Idle:
        session['stage'] = Stage.Chat
        return "进入*闲聊*模式，随便发点什么来聊天吧。退出请发送/q"


def chat(text, message):
    payload = {
        'key': 'free',
        'appid': 0,
        'msg': text,
    }
    r = requests.get('http://api.qingyunke.com/api.php', params=payload)
    return tts(r.json()['content'], message)


@robot.filter('智能画画')
def entry_ai_paint(message, session):
    if session['stage'] == Stage.Idle:
        session['stage'] = Stage.AIPaint
        return "进入*智能画画*模式，请描述你想画的画吧。比如：超现代飞船穿梭在赛博朋克的城市中，阴沉的天空下着小雨。退出请发送/q"


def ai_paint(text, message):
    filename = uuid.uuid4()
    prompt = fanyi.translate(text)
    img = stability.generate(prompt)
    img.save(f'./{filename}.png', 'PNG')
    with open(f'./{filename}.png', 'rb') as f:
        res = client.upload_media('image', f)
    os.remove(f'./{filename}.png')
    return ImageReply(
        message=message,
        media_id=res['media_id']
    )


@robot.text
def common(message, session):
    if not 'stage' in session or session['stage'] is None or session['stage'] == Stage.Idle:
        session['stage'] = Stage.Idle
        return Prompt
    else:
        text = message.content
        if text == '/q':
            res = f"已退出*{session['stage']}*模式，" + Prompt
            session['stage'] = Stage.Idle
            return res
        if session['stage'] == Stage.TTS:
            return tts(text, message)
        elif session['stage'] == Stage.Chat:
            return chat(text, message)
        elif session['stage'] == Stage.AIPaint:
            return ai_paint(text, message)


robot.config['HOST'] = '0.0.0.0'
robot.config['PORT'] = config.port
robot.run()

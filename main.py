import base64
import os
import re
import uuid
from enum import Enum
import shutil

import requests
import werobot
from tencentcloud.common import credential
from tencentcloud.tts.v20190823 import models, tts_client
from werobot.replies import ImageReply, VoiceReply

import config
import fanyi
import stability
from image import unet_cartoon, unet_artstyle, unet_sketch, unet_cartoon_handdrawn
from exif import get_brief_exif

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
    ViewExif = '查看照片信息'
    UNetCartoon = '人脸卡通化'
    UNetCartoonHanddrawn = '人脸卡通手绘'
    UNetSketch = '人脸素描化'
    UNetArtStyle = '人脸艺术化'


Prompt = """\
请发送关键词以进入相应模式：
    闲聊
    语音合成
    智能画画
    人脸卡通化
    人脸卡通手绘
    人脸素描化
    人脸艺术化
"""


def is_in_idle(session):
    return not 'stage' in session or session['stage'] is None or session['stage'] == Stage.Idle


def save_img_url_to_local(img_url, filename):
    r = requests.get(img_url, stream=True)
    if r.status_code == 200:
        with open(filename, 'wb') as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f)       

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
    if is_in_idle(session):
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
    if is_in_idle(session):
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
    if is_in_idle(session):
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


@robot.filter('查看照片信息')
def entry_unet_cartoon(message, session):
    if is_in_idle(session):
        session['stage'] = Stage.ViewExif
        return "进入*查看照片信息*模式，请直接发送你想查看信息的照片。退出请发送/q"


@robot.filter('人脸卡通化')
def entry_unet_cartoon(message, session):
    if is_in_idle(session):
        session['stage'] = Stage.UNetCartoon
        return "进入*人脸卡通化*模式，请直接发送你想卡通化的照片。退出请发送/q"


@robot.filter('人脸卡通手绘')
def entry_unet_cartoon_handdrawn(message, session):
    if is_in_idle(session):
        session['stage'] = Stage.UNetCartoonHanddrawn
        return "进入*人脸卡通手绘*模式，请直接发送你想卡通化的照片。退出请发送/q"


@robot.filter('人脸素描化')
def entry_unet_sketch(message, session):
    if is_in_idle(session):
        session['stage'] = Stage.UNetSketch
        return "进入*人脸素描化*模式，请直接发送你想素描化的照片。退出请发送/q"


@robot.filter('人脸艺术化')
def entry_unet_artstyle(message, session):
    if is_in_idle(session):
        session['stage'] = Stage.UNetArtStyle
        return "进入*人脸艺术化*模式，请直接发送你想艺术化的照片。退出请发送/q"


@robot.text
def common_text(message, session):
    if is_in_idle(session):
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
        elif session['stage'] == Stage.UNetCartoon:
            return "进入*人脸卡通化*模式，请直接发送你想卡通化的照片。退出请发送/q"
        elif session['stage'] == Stage.UNetCartoonHanddrawn:
            return "进入*人脸卡通手绘*模式，请直接发送你想卡通化的照片。退出请发送/q"
        elif session['stage'] == Stage.UNetSketch:
            return "进入*人脸素描化*模式，请直接发送你想卡通化的照片。退出请发送/q"
        elif session['stage'] == Stage.UNetArtStyle:
            return "进入*人脸艺术化*模式，请直接发送你想卡通化的照片。退出请发送/q"
        elif session['stage'] == Stage.ViewExif:
            return "进入*查看照片信息*模式，请直接发送你想查看信息的照片。退出请发送/q"


@robot.image
def common_image(message, session):
    if not 'stage' in session or session['stage'] is None or session['stage'] == Stage.Idle:
        session['stage'] = Stage.Idle
        return Prompt
    else:
        img_url = message.img
        if session['stage'] == Stage.UNetCartoon:
            out_path = f"./{uuid.uuid4()}.png"
            unet_cartoon(img_url, out_path)
            with open(out_path, 'rb') as f:
                res = client.upload_media('image', f)
            os.remove(out_path)
            return ImageReply(
                message=message,
                media_id=res['media_id']
            )
        elif session['stage'] == Stage.UNetCartoonHanddrawn:
            out_path = f"./{uuid.uuid4()}.png"
            unet_cartoon_handdrawn(img_url, out_path)
            with open(out_path, 'rb') as f:
                res = client.upload_media('image', f)
            os.remove(out_path)
            return ImageReply(
                message=message,
                media_id=res['media_id']
            )
        elif session['stage'] == Stage.UNetSketch:
            out_path = f"./{uuid.uuid4()}.png"
            unet_sketch(img_url, out_path)
            with open(out_path, 'rb') as f:
                res = client.upload_media('image', f)
            os.remove(out_path)
            return ImageReply(
                message=message,
                media_id=res['media_id']
            )
        elif session['stage'] == Stage.UNetArtStyle:
            out_path = f"./{uuid.uuid4()}.png"
            unet_artstyle(img_url, out_path)
            with open(out_path, 'rb') as f:
                res = client.upload_media('image', f)
            os.remove(out_path)
            return ImageReply(
                message=message,
                media_id=res['media_id']
            )
        elif session['stage'] == Stage.ViewExif:
            filename = f"./{uuid.uuid4()}.png"
            save_img_url_to_local(img_url, filename)
            with open(filename, 'rb') as f:
                tags = get_brief_exif(f)
            os.remove(filename)
            return '\n'.join([f"{key}： {tags[key]}" for key in tags.keys()])
        else:
            return '当前模式下不支持图片'


robot.config['HOST'] = '0.0.0.0'
robot.config['PORT'] = config.port
robot.run()

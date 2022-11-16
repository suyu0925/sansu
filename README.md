# 三苏杂物社
微信订阅号《三苏杂物社》的后台服务器代码

## 运行环境

因为工程依赖了[ModelScope](https://modelscope.cn/)，不能简单的`pip install -r ./requirements.txt`就完成环境安装。

请参见[ModelScope的环境安装](https://modelscope.cn/docs/%E7%8E%AF%E5%A2%83%E5%AE%89%E8%A3%85)。

## 环境变量

在运行前，需要先配置几个环境变量。

### 微信公众号
token, appid, appsecret是微信公众号后台开发的配置。

### 语音合成
语音合成使用的[腾讯云语音合成](https://cloud.tencent.com/product/tts)，所以需要腾讯云访问密匙。

### 智能画画
智能画画使用的stability的[dreamstudio](https://beta.dreamstudio.ai/dream)，需要stability的访问密匙。

### 中翻英
因为智能画画stability只支持英文，所以需要中翻英。使用的百度翻译。

## 运行

运行环境配置好后，直接`python main.py`运行。

如无需调试，建议使用`docker-compose up -d --build`运行。

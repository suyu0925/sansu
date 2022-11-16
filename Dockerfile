FROM registry.cn-hangzhou.aliyuncs.com/modelscope-repo/modelscope:ubuntu20.04-cuda11.3.0-py37-torch1.11.0-tf1.15.5-1.0.2

# need remove libnvidia-ml.so.1 and libcuda.so.1 on windows
RUN rm -rf /usr/lib/x86_64-linux-gnu/libnvidia-ml.so.1 /usr/lib/x86_64-linux-gnu/libcuda.so.1

WORKDIR /app

RUN python -m pip install -i https://pypi.mirrors.ustc.edu.cn/simple/ --upgrade pip

COPY requirements.txt requirements.txt
RUN pip install -i https://pypi.mirrors.ustc.edu.cn/simple/ -r requirements.txt

COPY . /app

CMD ["python", "main.py"]

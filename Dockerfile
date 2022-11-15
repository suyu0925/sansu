FROM python:3.9-slim

WORKDIR /app

RUN python -m pip install -i https://pypi.mirrors.ustc.edu.cn/simple/ --upgrade pip

COPY requirements.txt requirements.txt
RUN pip install -i https://pypi.mirrors.ustc.edu.cn/simple/ -r requirements.txt

COPY . /app

CMD ["python", "main.py"]

FROM python:3.7

ADD / /code

WORKDIR /code

RUN pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/ \
    && /bin/cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && echo 'Asia/Shanghai' >/etc/timezone

CMD ["python3", "/code/scan_mian.py"]

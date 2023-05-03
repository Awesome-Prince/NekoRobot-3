FROM python:3.10.1-buster

WORKDIR /root/Senku

COPY . .

RUN pip3 install --upgrade pip setuptools

RUN pip install -U -r requirements.txt

CMD ["python3","-m","NekoRobot"]

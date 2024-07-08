FROM python:3.10

RUN  apt update && apt install ffmpeg -y

WORKDIR /app

COPY requirements.txt .

RUN pip3 install -r requirements.txt

COPY . .


CMD ["python3", "./main.py"]
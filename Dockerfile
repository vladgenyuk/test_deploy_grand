from python:3.6

expose 8000

run mkdir /app

workdir /app

copy requirements.txt .

run pip install -r requirements.txt

copy . .

workdir svoy1

cmd gunicorn social.wsgi:application --log-file -
from python:3.6

expose 8000

run mkdir /app

workdir /app

copy requirements.txt .

run pip install --upgrade pip setuptools wheel
run pip install -r requirements.txt

copy . .

cmd python manage,py runserver

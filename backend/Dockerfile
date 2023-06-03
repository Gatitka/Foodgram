FROM python:3.7-slim

WORKDIR /app

COPY requirements.txt .
RUN python -m pip install --upgrade pip
# RUN sudo apt-get install libpq-dev

RUN pip3 install -r /app/requirements.txt --no-cache-dir

COPY . .

CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0:8000" ]

LABEL author='gatitka@yandex.ru' version=latest

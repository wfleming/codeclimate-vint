FROM python:3.5.1-alpine
MAINTAINER Code Climate <hello@codeclimate.com>

WORKDIR /usr/src/app

COPY ./requirements.txt /usr/src/app/
RUN pip install --quiet --requirement requirements.txt

RUN adduser -u 9000 app -D app

COPY . /usr/src/app

WORKDIR /code

USER app

VOLUME /code

CMD ["/usr/src/app/codeclimate-vint.py"]

FROM python:3

ENV TERM linux
ENV TERMINFO /etc/terminfo

RUN touch /var/log/access.log  # since the program will read this by default

COPY ./requirements.txt /usr/src/requirements.txt

WORKDIR /usr/src

RUN pip install -r requirements.txt

COPY . /usr/src
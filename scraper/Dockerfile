FROM python:3.6

COPY ./requirements.txt /scraper/requirements.txt
RUN pip install -r /scraper/requirements.txt
RUN rm /scraper/requirements.txt

RUN apt update
RUN apt install wait-for-it

COPY . /scraper

WORKDIR /scraper

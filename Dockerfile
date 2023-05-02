FROM python:3.10 as base
WORKDIR /src
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY scrapy.cfg .
COPY toys_scraper ./toys_scraper

CMD scrapy crawl jukate-spider

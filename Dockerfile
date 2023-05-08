FROM python:3.10 as base
WORKDIR /src
ENV PYTHONPATH="$PYTHONPATH:/src"
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY scrapy.cfg .
COPY toys_scraper ./toys_scraper

CMD python toys_scraper/runner.py

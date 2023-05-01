FROM python:3.10 as base
WORKDIR /src
COPY requirements.txt .
RUN pip install -r requirements.txt

CMD sleep 1000

FROM python:3.8

ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y --no-install-recommends \
		cron \
		rsyslog \
	&& rm -rf /var/lib/apt/lists/*

RUN cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && echo 'Asia/Shanghai'>/etc/timezone

RUN mkdir -p /opt/apps/ && mkdir -p /opt/data

WORKDIR /opt/apps/search_engine

COPY requirements.txt /tmp
RUN pip install -r /tmp/requirements.txt
RUN python -m nltk.downloader all
RUN pip install --upgrade urllib3

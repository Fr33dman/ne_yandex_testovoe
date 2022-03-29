FROM python:3.7-stretch

#RUN mkdir -p /var/app
COPY requirements.txt /var/app/requirements.txt
RUN pip install -r /var/app/requirements.txt

WORKDIR /var/app
VOLUME /var/app

COPY alembic.ini /var/app/alembic.ini
COPY entrypoint.sh /entrypoint.sh
COPY . /var/app/

RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]

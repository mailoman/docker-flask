
FROM ubuntu:14.04

MAINTAINER Alex <mailoman2008@gmail.com>

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update
RUN apt-get -y install curl nginx sed python-pip python-dev uwsgi-plugin-python supervisor

RUN pip install MySQL-python Flask-SQLAlchemy Flask-Migrate flask-cli Flask-Security Flask-Admin Flask-JSON Flask-Autodoc

RUN mkdir -p /var/log/nginx/app
RUN mkdir -p /var/log/uwsgi/app


RUN rm /etc/nginx/sites-enabled/default
COPY flask.conf /etc/nginx/sites-available/
RUN ln -s /etc/nginx/sites-available/flask.conf /etc/nginx/sites-enabled/flask.conf
COPY uwsgi.ini /var/www/app/
RUN echo "daemon off;" >> /etc/nginx/nginx.conf


RUN mkdir -p /var/log/supervisor
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

copy app /var/www/app
RUN pip install -r /var/www/app/requirements.txt

EXPOSE 80

CMD ["/usr/bin/supervisord"]

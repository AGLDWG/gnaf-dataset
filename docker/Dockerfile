FROM alpine:3.9

RUN apk --no-cache add tini-static busybox-suid python3 libxml2 py3-lxml uwsgi uwsgi-python3 postgresql
RUN apk --no-cache add --virtual .build-dependencies postgresql-dev python3-dev musl-dev gcc

RUN mkdir -p /deploy
RUN chown -R uwsgi:uwsgi /deploy
ADD ./requirements.txt /deploy/
RUN mkdir -p /deploy/gnaf/
ADD ./_config /deploy/gnaf/_config
ADD ./_docs /deploy/gnaf/_docs
ADD ./controller /deploy/gnaf/controller
ADD ./model /deploy/gnaf/model
ADD ./view /deploy/gnaf/view
ADD ./__init__.py ./app.py ./db.py /deploy/gnaf/
WORKDIR /deploy

RUN python3 -m ensurepip
RUN pip3 install --no-cache-dir -r requirements.txt
RUN apk del .build-dependencies
RUN echo $'import sys\n\
import logging\n\
sys.path.insert(0, "/deploy/gnaf")\n\
sys.path.insert(0, "/deploy")\n\
logging.basicConfig(stream=sys.stderr)\n\
from gnaf.app import app as application\n' > wsgi.py

RUN chown -R uwsgi:uwsgi /deploy
RUN chmod -R 777 /deploy
RUN chmod a+x ./wsgi.py ./gnaf/app.py

RUN echo $'ini = :python3_gnaf_ldapi\n\
\n[python3_gnaf_ldapi]\n\
plugins = python3\n\
callable = application\n\
wsgi-file = wsgi.py\n' >> /etc/uwsgi/uwsgi.ini

RUN mkdir -p /var/run/uwsgi
RUN chown -R uwsgi:uwsgi /var/run/uwsgi
RUN chmod -R 777 /var/run/uwsgi
VOLUME /var/run/uwsgi
CMD ["uwsgi", "--ini", "/etc/uwsgi/uwsgi.ini", "--master", "--workers", "2", "--protocol", "uwsgi", "--enable-threads", "--chmod-socket=666", "--socket", "/var/run/uwsgi/uwsgi.sock"]
ENTRYPOINT [ "/sbin/tini-static" ]

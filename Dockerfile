FROM acait/django-container:backwards-compat-python2 as django

USER root
RUN apt-get update && apt-get install mysql-client libmysqlclient-dev -y
USER acait

ADD --chown=acait:acait endorsement/VERSION /app/endorsement/
ADD --chown=acait:acait setup.py /app/
ADD --chown=acait:acait requirements.txt /app/

RUN . /app/bin/activate && pip install -r requirements.txt
RUN . /app/bin/activate && pip install mysqlclient 

ADD --chown=acait:acait . /app/
ADD --chown=acait:acait docker/ project/
RUN . /app/bin/activate && pip install nodeenv && nodeenv -p &&\
    npm install -g npm &&\
    ./bin/npm install less -g 
RUN . /app/bin/activate && python manage.py collectstatic --noinput && python manage.py compress

ENV REMOTE_USER jstaff

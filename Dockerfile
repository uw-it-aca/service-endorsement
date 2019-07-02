FROM acait/django-container:develop as django

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
RUN . /app/bin/activate && pip install django-webpack-loader
# RUN . /app/bin/activate && pip install nodeenv && nodeenv -p &&\
#     npm install -g npm &&\
#     ./bin/npm install less -g 
# RUN . /app/bin/activate && python manage.py collectstatic --noinput && python manage.py compress

FROM node:8.15.1-jessie AS wpack
ADD . /app/
WORKDIR /app/
RUN npm install .
# RUN npm install handlebars-loader --save
RUN npx webpack --verbose --mode=production

FROM django

COPY --chown=acait:acait --from=wpack /app/endorsement/static/endorsement/bundles/* /app/endorsement/static/prereq_map/bundles/
COPY --chown=acait:acait --from=wpack /app/endorsement/static/ /static/
COPY --chown=acait:acait --from=wpack /app/endorsement/static/webpack-stats.json /app/endorsement/static/webpack-stats.json
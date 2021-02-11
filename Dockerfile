FROM gcr.io/uwit-mci-axdd/django-container:1.2.8 as app-prewebpack-container

USER root
RUN apt-get update && apt-get install mysql-client libmysqlclient-dev libpq-dev -y
USER acait

ADD --chown=acait:acait endorsement/VERSION /app/endorsement/
ADD --chown=acait:acait setup.py /app/
ADD --chown=acait:acait requirements.txt /app/

RUN . /app/bin/activate && pip install -r requirements.txt

ADD --chown=acait:acait . /app/
ADD --chown=acait:acait docker/ project/
RUN . /app/bin/activate && pip install django-webpack-loader
RUN . /app/bin/activate && python manage.py collectstatic

FROM node:8.15.1-jessie AS wpack
ADD . /app/
WORKDIR /app/
RUN npm install .
RUN npx webpack --mode=production

FROM app-prewebpack-container as app-container

COPY --chown=acait:acait --from=wpack /app/endorsement/static/endorsement/bundles/* /app/endorsement/static/endorsement/bundles/
COPY --chown=acait:acait --from=wpack /app/endorsement/static/ /static/
COPY --chown=acait:acait --from=wpack /app/endorsement/static/webpack-stats.json /app/endorsement/static/webpack-stats.json

FROM gcr.io/uwit-mci-axdd/django-test-container:1.2.8 as app-test-container

COPY --from=app-container /app/ /app/
COPY --from=app-container /static/ /static/

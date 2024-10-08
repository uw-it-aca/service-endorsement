ARG DJANGO_CONTAINER_VERSION=1.4.1

FROM us-docker.pkg.dev/uwit-mci-axdd/containers/django-container:${DJANGO_CONTAINER_VERSION} AS app-prewebpack-container

USER root
RUN apt-get update && apt-get install mysql-client libmysqlclient-dev libpq-dev -y
USER acait

ADD --chown=acait:acait endorsement/VERSION /app/endorsement/
ADD --chown=acait:acait setup.py /app/
ADD --chown=acait:acait requirements.txt /app/

RUN . /app/bin/activate && pip install -r requirements.txt

ADD --chown=acait:acait . /app/
ADD --chown=acait:acait docker/ project/

ADD --chown=acait:acait docker/app_start.sh /scripts
RUN chmod u+x /scripts/app_start.sh

RUN . /app/bin/activate && pip install django-webpack-loader
RUN . /app/bin/activate && python manage.py collectstatic

FROM node:lts-slim AS node-bundler
ADD . /app/
WORKDIR /app/
RUN npm install .
RUN npx webpack --mode=production

FROM app-prewebpack-container AS app-container

COPY --chown=acait:acait --from=node-bundler /app/endorsement/static/endorsement/bundles/* /app/endorsement/static/endorsement/bundles/
COPY --chown=acait:acait --from=node-bundler /app/endorsement/static/ /static/
COPY --chown=acait:acait --from=node-bundler /app/endorsement/static/webpack-stats.json /app/endorsement/static/webpack-stats.json

FROM us-docker.pkg.dev/uwit-mci-axdd/containers/django-test-container:${DJANGO_CONTAINER_VERSION} AS app-test-container

COPY --from=app-container /app/ /app/
COPY --from=app-container /static/ /static/

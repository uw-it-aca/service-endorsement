#!/bin/sh

# travis test script for django app

#
# PRECONDITION: env var DJANGO_APP 
# exists in the calling travis shell
#

# install test tooling
source bin/activate
pip install pycodestyle coveralls
apt-get install -y nodejs npm
npm install -g jshint


TEST="pycodestyle ${DJANGO_APP}/ --exclude=migrations,static"
echo TEST: ${TEST}
eval $TEST

if [ -d ${DJANGO_APP}/static/${DJANGO_APP}/js ]; then
    TEST="jshint ${DJANGO_APP}/static/${DJANGO_APP}/js --verbose"
    echo TEST: ${TEST}
    eval $TEST
elif [ -d ${DJANGO_APP}/static/js ]; then
    TEST="jshint ${DJANGO_APP}/static/js --verbose"
    echo TEST: ${TEST}
    eval $TEST
fi

TEST="coverage run --source=${DJANGO_APP} '--omit=*/migrations/*' manage.py test ${DJANGO_APP}"
echo TEST: ${TEST}
eval $TEST

# put generaged coverage result where it will get processed
cp .coverage /coverage/.coverage

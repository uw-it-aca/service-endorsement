#!/bin/sh

# test script for service-endorsement

# install test tooling
. bin/activate && pip install pycodestyle coveralls
apt-get install -y nodejs npm
npm install -g jshint


TEST='. bin/activate && pycodestyle endorsement/ --exclude=migrations,static'
echo TEST: ${TEST}
eval $TEST

TEST='jshint endorsement/static/endorsement/js/ --verbose'
echo TEST: ${TEST}
eval $TEST

TEST='. bin/activate && coverage run --source=endorsement/ '--omit=endorsement/migrations/*' manage.py test endorsement'
echo TEST: ${TEST}
eval $TEST

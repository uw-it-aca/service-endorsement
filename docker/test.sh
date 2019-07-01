#!/bin/sh

# test script for service-endorsement

# install test tooling
pip install pycodestyle
pip install coveralls
apt-get install -y nodejs npm
npm install -g jshint


TEST='pycodestyle endorsement/ --exclude=migrations,static'
echo TEST: ${TEST}
eval $TEST

TEST='jshint endorsement/static/endorsement/js/ --verbose'
echo TEST: ${TEST}
eval $TEST

TEST='. bin/activate && coverage run --source=endorsement/ '--omit=endorsement/migrations/*' manage.py test endorsement'
echo TEST: ${TEST}
eval $TEST

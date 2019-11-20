#!/bin/sh
set -e
trap 'exit 1' ERR

# travis test script for django app
#
# PRECONDITION: inherited env vars from application's .travis.yml MUST include:
#      DJANGO_APP: django application directory name

# start virtualenv
source bin/activate

# install test tooling
pip install pycodestyle coverage
apt-get install -y nodejs npm
npm install -g jshint

function run_test {
    echo "##########################"
    echo "TEST: $1"
    eval $1
}

run_test "pycodestyle ${DJANGO_APP}/ --exclude=migrations,static"

if [ -d ${DJANGO_APP}/static/${DJANGO_APP}/js ]; then
    run_test "jshint ${DJANGO_APP}/static/${DJANGO_APP}/js --verbose"
elif [ -d ${DJANGO_APP}/static/js ]; then
    run_test "jshint ${DJANGO_APP}/static/js --verbose"
fi

run_test "coverage run --source=${DJANGO_APP} '--omit=*/migrations/*' manage.py test ${DJANGO_APP}"

# put generaged coverage result where it will get processed
cp .coverage.* /coverage

exit 0

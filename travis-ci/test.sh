#!/bin/sh
set -e
trap 'travis_terminate 1' ERR

# travis test script for django app

DJANGO_APP=$1

# install test tooling
source bin/activate
pip install pycodestyle coveralls
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

echo "run coveralls"
coveralls

exit 0

# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import os
from setuptools import setup

README = """
See the README on `GitHub
<https://github.com/uw-it-aca/service-endorsement>`_.
"""

# The VERSION file is created by travis-ci, based on the tag name
version_path = 'endorsement/VERSION'
VERSION = open(os.path.join(os.path.dirname(__file__), version_path)).read()
VERSION = VERSION.replace("\n", "")

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

url = "https://github.com/uw-it-aca/service-endorsement"
setup(
    name='ServiceEndorsement',
    version=VERSION,
    packages=['endorsement'],
    author="UW-IT AXDD",
    author_email="aca-it@uw.edu",
    include_package_data=True,
    install_requires=[
        'django~=5.2',
        'djangorestframework==3.17.2',
        'ordereddict',
        'simplejson',
        'django-webpack-loader==1.4.0',
        'django-userservice~=3.2',
        'urllib3~=1.26',
        'psycopg[c]',
        'uw-memcached-clients~=1.1',
        'uw-restclients-core~=1.4',
        'uw-restclients-pws==2.1',
        'uw-restclients-gws~=2.3',
        'uw-restclients-uwnetid~=1.1',
        'uw-restclients-django-utils~=2.3',
        'uw-restclients-itbill~=0.1',
        'uw-restclients-msca~=0.2',
        'django-safe-emailbackend~=1.2',
        'uw-django-saml2~=1.8',
        'django-pyscss',
        'django-supporttools~=3.5',
        'django-persistent-message~=1.3',
        'django_client_logger~=3.1',
    ],
    license='Apache License, Version 2.0',
    description=('App mangaging University of Washington Endorsed Services'),
    long_description=README,
    url=url,
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
)

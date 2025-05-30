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
        'Django~=3.2',
        'djangorestframework==3.15.1',
        'ordereddict',
        'simplejson',
        'django-webpack-loader>=1.0,<2.0',
        'django-userservice<4.0',
        'urllib3~=1.26',
        'unittest2',
        'pytz',
        'psycopg2>=2.8,<2.9',
        'lxml~=4.9.1',
        'xmlsec==1.3.13',
        'uw-memcached-clients~=1.0.5',
        'UW-RestClients-Core~=1.3.3',
        'UW-Restclients-PWS==2.0.2',
        'UW-RestClients-GWS~=2.0.1',
        'UW-RestClients-UWNetID~=1.1.2',
        'UW-RestClients-Django-Utils~=2.1.5',
        'UW-RestClients-ITBill~=0.1',
        'UW-RestClients-MSCA~=0.1.5',
        'Django-Safe-EmailBackend~=1.2',
        'UW-Django-SAML2>=1.3.8,<2.0',
        'django-pyscss',
        'Django-SupportTools~=3.5',
        'Django-Persistent-Message',
        'django_client_logger~=2.0',
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

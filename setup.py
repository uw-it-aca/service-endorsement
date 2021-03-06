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
        'Django~=2.2',
        'ordereddict',
        'simplejson',
        'django-webpack-loader',
        'django-userservice<4.0,>3.1',
        'urllib3>=1.25.3,<1.26',
        'unittest2',
        'pytz',
        'psycopg2',
        'lxml==4.2.5,<4.3',
        'uw-memcached-clients~=1.0.5',
        'UW-RestClients-Core~=1.3.3',
        'UW-Restclients-PWS==2.0.2',
        'UW-RestClients-GWS~=2.0.1',
        'UW-RestClients-UWNetID~=1.0.7',
        'UW-RestClients-Django-Utils~=2.1.5',
        'Django-Safe-EmailBackend~=1.1.1',
        'UW-Django-SAML2>=1.3.8,<2.0',
        'djangorestframework>=3.6.4',
        'django-pyscss',
        'Django-SupportTools~=3.4',
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
        'Programming Language :: Python :: 3.6',
    ],
)

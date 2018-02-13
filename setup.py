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
        'Django==1.10.5',
        'ordereddict',
        'simplejson',
        'django-compressor',
        'BeautifulSoup',
        'urllib3==1.10.2',
        'django-templatetag-handlebars',
        'unittest2',
        'AuthZ-Group',
        'UW-RestClients-Core<1.0,>=0.9.3',
        'UW-RestClients-PWS<1.0,>=0.6',
        'UW-RestClients-GWS<1.0',
        'UW-RestClients-UWNetID<1.0',
        'django-userservice==1.2.1',
        'django-pyscss',
        'django_mobileesp',
        'Django-SupportTools',
        'django_client_logger',
    ],
    license='Apache License, Version 2.0',
    description=('App mangaging University of Washington endorsed services'),
    long_description=README,
    url=url,
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
    ],
)

import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-id',
    version='0.01',
    packages=['id'],
    include_package_data=True,
    license='Apache License',
    description=README,
    long_description='A simple Django app to conduct Web-based id.',
    url='https://github.com/kostya-ten/django-id',
    author='Kostya Ten',
    author_email='kostya@yandex.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 2.1',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    install_requires=[
        'Django >= 2.2',
        'Pillow >= 6.0.0',
        'phonenumbers >= 8.10.6',
        'email - validator >= 1.0.3',
        'timezonefinder >= 4.0.2',
        'geoip2 >= 2.9.0',
        'requests >= 2.21.0',
    ]
)
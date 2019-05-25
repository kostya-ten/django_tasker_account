import io
import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

with io.open("README.rst", encoding="UTF-8") as readme:
    long_description = readme.read()
    
setup(
    name='django-tasker-account',
    version='0.0.1',
    packages=[
        'tests',
        'django_tasker_account',
        'django_tasker_account.migrations',
        'django_tasker_account.templates',
        'django_tasker_account.templates.django_tasker_account',
        'django_tasker_account.management.commands',
    ],
    include_package_data=True,
    license='Apache License 2.0',
    description="Django Tasker Account - Extended user system for Django",
    long_description=long_description,
    url='https://github.com/kostya-ten/django_tasker_account/',
    author='Kostya Ten',
    author_email='kostya@yandex.ru',
    classifiers=[
        'Environment :: Web Environment',
        'Natural Language :: English',
        'Natural Language :: Russian',
        'Framework :: Django',
        'Framework :: Django :: 2.1',
        'Framework :: Django :: 2.2',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'License :: OSI Approved :: Apache Software License',
    ],
    project_urls={
        'Documentation': 'https://django-tasker-account.readthedocs.io/',
        'Source': 'https://github.com/kostya-ten/django_tasker_account/',
        'Tracker': 'https://github.com/kostya-ten/django_tasker_account/issues',
    },
    python_requires='>=3'
)

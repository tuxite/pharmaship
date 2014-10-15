# -*- coding: utf-8 -*-
from distutils.core import setup
from setuptools import find_packages

setup(
    name='pharmaship',
    version='0.9',
    author=u'Matthieu Morin',
    author_email='morinmatthieu@gmail.com',
    packages=find_packages(),
    include_package_data=True,
    url='https://github.com/tuxite/pharmaship',
    license='GPL licence, see LICENCE.txt',
    description='A pharmacy software for merchant ships',
    long_description=open('README.md').read(),
    zip_safe=False,
    install_requires=[
        'django',
        'weasyprint',
        'python-gnupg',
        'MySQL-python',
        'PyYAML',
        ],
)

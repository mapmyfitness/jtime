#! /usr/bin/env python

from setuptools import setup, find_packages

import jtime

setup(
    name=jtime.__name__,
    version=jtime.__version__,
    description=jtime.__description__,
    long_description=open('README.md').read(),
    classifiers=[],
    keywords='',
    author=jtime.__author__,
    author_email='',
    url=jtime.__url__,
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    zip_safe=False,
    test_suite='nose.collector',
    install_requires=open('requirements.txt').read().splitlines(),
    tests_require=open('test_requirements.txt').read().splitlines(),
    setup_requires=[],
    entry_points={
        'console_scripts': [
            'jtime = jtime.jtime:main',
        ]
    },
    namespace_packages=[],
)

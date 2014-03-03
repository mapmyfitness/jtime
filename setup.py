#! /usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='jtime',
    version='0.1',
    description="Jira time tracking tool built on the command line to take context from your various git repositories.",
    long_description="Jira time tracking tool built on the command line to take context from your various git repositories.",
    classifiers=[], 
    keywords='',
    author='MapMyFitness',
    author_email='',
    url='https://github.com/bnekolny/jtime',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    zip_safe=False,
    test_suite='nose.collector',
    install_requires=[
        ### Required to build documentation
        # "Sphinx >= 1.0",
        ### General requirements -- TODO: pin versions
        "jira",
        "GitPython==0.1.7",
        "python-dateutil",
        "argh",
        "argcomplete",
        ],
    setup_requires=[],
    entry_points={
        'console_scripts': [
            'jtime = jtime.jtime:main',
        ]
    },
    namespace_packages=[],
    )

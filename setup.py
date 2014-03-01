
from setuptools import setup, find_packages
import sys, os

setup(name='jtime',
    version='0.1',
    description="Jira time tracking tool built on the command line to take context from your various git repositories.",
    long_description="Jira time tracking tool built on the command line to take context from your various git repositories.",
    classifiers=[], 
    keywords='',
    author='MapMyFitness',
    author_email='',
    url='https://github.com/bnekolny/jtime',
    license='GNU GENERAL PUBLIC LICENSE Version 2',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    zip_safe=False,
    test_suite='nose.collector',
    install_requires=[
        ### Required to build documentation
        # "Sphinx >= 1.0",
        ### Required for testing
        # "nose",
        # "coverage",
        ],
    setup_requires=[],
    entry_points="""
    """,
    namespace_packages=[],
    )

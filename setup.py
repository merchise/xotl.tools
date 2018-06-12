#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# flake8:  noqa
import os
import sys
from setuptools import setup, find_packages

try:
    execfile
except NameError:
    def execfile(filename):
        'To run in Python 3'
        import builtins
        exec_ = getattr(builtins, 'exec')
        with open(filename, "rb") as f:
            code = compile(f.read().decode('utf-8'), filename, 'exec')
            return exec_(code, globals())


# Import the version from the release module
project_name = 'xoutil'
_current_dir = os.path.dirname(os.path.abspath(__file__))
release = os.path.join(_current_dir, project_name, 'release.py')
execfile(release)
version = VERSION  # noqa

if RELEASE_TAG != '':   # noqa
    dev_classifier = 'Development Status :: 4 - Beta'
else:
    dev_classifier = 'Development Status :: 5 - Production/Stable'

from setuptools.command.test import test as TestCommand


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)

setup(
    name=project_name,
    version=version,
    description=("Collection of usefull algorithms and other very "
                 "disparate stuff"),
    long_description=open(os.path.join(_current_dir, 'README.rst')).read(),
    classifiers=[
        # Get from http://pypi.python.org/pypi?%3Aaction=list_classifiers
        dev_classifier,
        'Intended Audience :: Developers',
        ('License :: OSI Approved :: '
         'GNU General Public License v3 or later (GPLv3+)'),
        'Operating System :: POSIX :: Linux',  # This is where we are
                                               # testing. Don't promise
                                               # anything else.
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords='',
    author='Merchise',
    author_email='project+xoutil@merchise.org',
    # TODO: @med, @manu Negotiate with Maykel Moya to obtain plain "Merchise"
    #       folder at "https://github.com"
    url='https://github.com/merchise-autrement/xoutil/',
    license='GPLv3+',
    tests_require=['pytest'],
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    zip_safe=False,
    python_requires='>=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*',
    install_requires=[
        'monotonic; python_version<"3.3"',
        'contextlib2; python_version<"3.4"',
    ],
    extras_require={
        'recommended': [
            'python-dateutil',
            'enum34; python_version<"3.4"'
        ],
    },
    cmdclass={'test': PyTest},
)

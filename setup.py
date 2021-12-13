#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# flake8:  noqa
import os
import sys
import versioneer

from setuptools import setup, find_packages

try:
    execfile
except NameError:

    def execfile(filename):
        "To run in Python 3"
        import builtins

        exec_ = getattr(builtins, "exec")
        with open(filename, "rb") as f:
            code = compile(f.read().decode("utf-8"), filename, "exec")
            return exec_(code, globals())


# Import the version from the release module
project_name = "xotl.tools"
_current_dir = os.path.dirname(os.path.abspath(__file__))
dev_classifier = "Development Status :: 5 - Production/Stable"

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


_cmdclass = {"test": PyTest}
_cmdclass.update(versioneer.get_cmdclass())

recommended_requirements = ["python-dateutil"]
docs_requirements = recommended_requirements + [
    "hypothesis~=6.31",
    "pytz",
    "sphinx~=4.3.1",
    "sphinx-rtd-theme",
]
dev_requirements = docs_requirements + [
    "flake8>=3.8.4",
    "flake8-bugbear~=21.4.3",
    "black==21.5b2",
    "isort~=5.9.3",
    "tox",
]


setup(
    name=project_name,
    version=versioneer.get_version(),
    description=("Collection of usefull algorithms and other very " "disparate stuff"),
    long_description=open(os.path.join(_current_dir, "README.rst")).read(),
    classifiers=[
        # Get from http://pypi.python.org/pypi?%3Aaction=list_classifiers
        dev_classifier,
        "Intended Audience :: Developers",
        ("License :: OSI Approved :: " "GNU General Public License v3 or later (GPLv3+)"),
        "Operating System :: POSIX :: Linux",  # This is where we are
        # testing. Don't promise
        # anything else.
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="",
    author="Merchise Autrement",
    url="https://gitlab.merchise.org/merchise/xotl.tools",
    license="GPLv3+",
    tests_require=["pytest"],
    namespace_packages=["xotl"],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    python_requires=">=3.7",
    install_requires=[
        "typing-extensions~=3.10.0",
    ],
    extras_require={
        "recommended": recommended_requirements,
        "dev": dev_requirements,
        "docs": docs_requirements,
    },
    cmdclass=_cmdclass,
)

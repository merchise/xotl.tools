#!/usr/bin/env python
import os, sys
from setuptools import setup, find_packages

# Import the version from the release module
project_name = 'xoutil'
_current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(_current_dir, project_name))
from release import VERSION as version

setup(name=project_name,
      version=version,
      description="Collection of usefull algorithms and other very disparate "
                  "stuff",
      long_description=open(os.path.join('docs', 'readme.txt')).read(),
      classifiers=[
        # Get from http://pypi.python.org/pypi?%3Aaction=list_classifiers
            'Development Status :: 5 - Stable',
            'Intended Audience :: Developers',
            'License :: GPL',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
        ],
      keywords='',
      author='Merchise Autrement',
      author_email='merchise.h8@gmail.com',
      url='http://www.merchise.org/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
      ],
      entry_points="""
      """,
      )

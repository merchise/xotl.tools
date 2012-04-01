#!/usr/bin/env python
from setuptools import setup, find_packages

version = '1.0.17'

setup(name='xoutil',
      version=version,
      description="Collection of usefull algorithms and other very disparate "
                  "stuff",
      long_description='',
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
      package_data={
        'xoutil': ['paste/templates/*.*',
                   'paste/templates/**/*.*',
                   'paste/templates/**/**/*.*']
      },
      zip_safe=False,
      install_requires=[
      ],
      entry_points="""
        [paste.paster_create_template]
            merchise = xoutil.paste.template:MerchisePackageTemplate
      """,
      )

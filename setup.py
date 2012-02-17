from setuptools import setup, find_packages

version = '1.0.10'

setup(name='xoutil',
      version=version,
      description="Collection of usefull algorithms and other very disparate stuff",
      long_description='',
      classifiers=[
            # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
            'Development Status :: 5 - Stable',
            'Intended Audience :: Developers',
            'License :: GPL',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
        ],
      keywords='',
      author='Merchise Autrement',
      author_email='merchise.h8@gmail.com',
      url='',
      license='GPL',
      packages=find_packages(exclude=['ez_setup', 'examples', ]),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        # 'zope.interface',
      ],
      entry_points="""
      """,
      )

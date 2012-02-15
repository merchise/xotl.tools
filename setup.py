from setuptools import setup, find_packages

version = '1.0.4'

setup(name='xoutil',
      version=version,
      description="Collection of usefull algorithms and other very disparate stuff",
      long_description='',
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
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

from setuptools import setup, find_packages

version = '0.1-dev'

setup(name='ezjaildeploy',
      version=version,
      description="a Python API for ezjail",
      long_description=(
          open('README.rst').read()),
      classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX :: BSD :: FreeBSD',
        'Programming Language :: Python',
        'Topic :: System :: Systems Administration',
      ],  # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='ezjail, FreeBSD, fabric',
      author='Tom Lazar',
      author_email='tom@tomster.org',
      url='https://github.com/tomster/ezjail-deploy',
      license='BSD',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        "ezjailremote",
        "mr.bob",
        "docopt",
          # -*- Extra requirements: -*-
      ],
      extras_require={
          'tests': ['unittest2', 'pytest']
      },
      entry_points="""
      # -*- Entry points: -*-
        [console_scripts]
        ezjail-deploy=ezjaildeploy.commandline:main
      """,
      )

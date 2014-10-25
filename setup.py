from setuptools import setup, find_packages

# setup
setup(
  name='python-streamtools',
  version='0.0.9.6.1',
  description='A python wrapper for streamtools: http://nytlabs.github.io/streamtools',
  long_description = "",
  classifiers=[
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python",
    ],
  keywords='',
  author='Brian Abelson',
  author_email='brian@newslynx.org',
  url='http://github.com/abelsonlive/python-streamtools',
  license='MIT',
  packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
  namespace_packages=[],
  include_package_data=False,
  zip_safe=False,
  install_requires=[
    "requests",
    "ujson"
  ],
  tests_require=[]
)
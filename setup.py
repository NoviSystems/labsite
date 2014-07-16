import os
from setuptools import setup, find_packages

def read(fname):
  return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name="foodapp",
    version="0.1",
    author="OSCAR Lab",
    packages=find_packages(),
    include_package_data=True,
    long_description=read('README.md'),
    install_requires=[
        "celery",
        "south",
    ],
)

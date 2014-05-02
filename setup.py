import os
from setuptools import setup, find_packages

def read(fname):
  return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "foodapp",
    version = "0.1",
    author = "OSCAR Lab",
    packages = find_packages(),
    # long_description=read('README.md'),
    package_data = {
        'foodapp': [
            'fixtures/*',
            'static/*',
            'templates/*',
        ],
    },
    install_requires=[
        "django>=1.5",
        "south",
    ],
)

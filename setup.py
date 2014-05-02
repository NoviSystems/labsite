import os
from setuptools import setup

def read(fname):
  return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "foodapp",
    version = "0.1",
    author = "OSCAR Lab",
    packages=['foodapp'],
    long_description=read('README'),
    package_data = {
        'foodapp': [
            'templates/foodapp/*',
        ],
    }
    install_requires=[
        "django>=1.5",
        "south",
    ],
)

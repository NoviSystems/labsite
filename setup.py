import io
import sys

from setuptools import setup, find_packages


assert 'upload' not in sys.argv, \
    'Not intended for public distribution.'


def get_long_description():
    with io.open('README.md', encoding='utf-8') as f:
        return f.read()


requirements = [
    # Project config
    'django~=1.11',
    'django-environ>=0.4.3',
    'colorlog',

    # Django applications
    'djangorestframework<3.8',
    'djangorestframework-filters<1',
    'django-admin-rangefilter',
    'django-fsm',
    'django-registration',
    'django-registration-invite',
    'django-template-forms',

    # Additional dependencies
    'celery[redis]',
    'stripe',
]


setup(
    name='labsite',
    version='0.0.0',
    author='ITNG',
    url='https://github.com/ITNG/labsite',
    description='ITNG lab website',
    long_description=get_long_description(),
    package_dir={'': 'src'},
    packages=find_packages('src'),
    include_package_data=True,
    install_requires=requirements,
    extras_require={
        'sentry': ['raven'],
        'dev': ['tox', 'tox-venv', 'pip-tools'],
    },
    entry_points={
        'console_scripts': [
            'labsite = labsite.__main__:main',
            'labsite-setup = labsite.__main__:init',
        ],
    },
)


from fabtools import vagrant

__all__ = [
    'on',
]

on = vagrant.vagrant
on.name = 'on'
on.default = True

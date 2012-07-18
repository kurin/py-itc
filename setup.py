#!/usr/bin/env python

from distutils.core import setup
import itc

setup(
        name='py-itc',
        version=itc.__version__,
        description='Interval Tree Clock',
        author='Toby Burress',
        author_email='kurin@delete.org',
        url='https://github.com/kurin/py-itc/',
        py_modules=['itc']
    )

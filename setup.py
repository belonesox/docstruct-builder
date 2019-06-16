#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
 Setup for the package
"""

from setuptools import setup
setup(
    entry_points={
        'console_scripts': [
            'dsb=docstruct_builder:main',
        ],
    },
    name='docstruct_builder',
    version='0.10',
    packages=['docstruct_builder'],
    author_email = "stanislav.fomin@gmail.com",

)


# -*- coding: utf-8 -*-
"""
Created on Fri Mar 17 13:23:56 2023

@author: Julu

"""

from setuptools import setup

setup(
    name='art-daq',
    version='1.0.4',
    description='Paquete para usar la tarjeta de NI, USB-6001',
    packages=['art_daq'],
    install_requires=[
        'nidaqmx',
        'matplotlib',
        'numpy'
    ],
    
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Education',
        'License :: OSI Approved :: MIT License',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    
    url='https://github.com/Julumisan/art-daq',
    author='Juan Luis',
    author_email='julumisan@gmail.com'
)

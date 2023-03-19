# -*- coding: utf-8 -*-
"""
Created on Fri Mar 17 13:23:56 2023

@author: julu

"""

from setuptools import setup

setup(
    name='art-daq',
    version='0.2.0',
    description='Paquete para usar la tarjeta de NI, USB-6001',
    packages=['Script'],
    install_requires=[
        'nidaqmx',
    ],
    
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Education',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    
    url='https://github.com/Julumisan/art-daq',
    author='Juan Luis',
    author_email='julumisan@gmail.com'
)

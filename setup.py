#-*- encoding: utf-8 -*-
from setuptools import setup
setup(name="python-carteblanche",
      version="0.0.1",
      description="Module to hold and serialize the in-memory relationship between urls and objects and users.",
      url="https://github.com/neuman/python-carteblanche",
      maintainer='Eric Neuman',
      maintainer_email='eric@indiepen.net',
      packages=["carteblanche",
                "carteblanche.models",
                "carteblanche.tests"],
      install_requires=[],
      platforms=['Any'],
      keywords=['django', 'py-money', 'money'],
      classifiers=["Development Status :: 5 - Production/Stable",
                   "Intended Audience :: Developers",
                   "License :: OSI Approved :: BSD License",
                   "Operating System :: OS Independent",
                   "Programming Language :: Python",
                   "Framework :: Django", ]
      )
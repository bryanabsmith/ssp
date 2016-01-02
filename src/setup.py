#!/usr/bin/python

# Courtesy of https://bitbucket.org/anthony_tuininga/cx_freeze/src/1282b6b6ee637738210113dd88c3c198d475340f/cx_Freeze/samples/simple/setup.py?at=default
from cx_Freeze import setup, Executable

executables = [
    Executable("ssp.py")
]

setup(name="ssp",
      version="0.1",
      description="Summer Server Project web server",
      executables=executables)
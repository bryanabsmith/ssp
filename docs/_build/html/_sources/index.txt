About
===

Version 0.1


Supported Platforms
===================

|Windows 10|OS X 10.11|Linux|FreeBSD 10.2|
|---|---|---|---|

_NOTE: This is the list of platform versions that have been tested. It is very possible that it works on other versions and indeed, it likely does._


Getting the Source
==================

> git clone https://github.com/bryanabsmith/ssp.git

This will clone the repo for you.

You'll also need python-requests and python-netifaces:

> pip install requests netifaces

Technically, these are not required if you don't need to get your external IP (requests) and/or you don't run ssp on Linux or FreeBSD (netifaces).

Running
=======

Simply execute src/ssp.py to run ssp:

> python ssp.py

It's likely that the default configuration, outlined in ssp.config, will not work as you want it to out of the box.

Configuration Options
=====================

Setup
-----

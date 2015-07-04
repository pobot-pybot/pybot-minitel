''pybot'' collection
====================

This package is part of POBOT's `pybot` packages collection, which aims
at gathering contributions created while experimenting with various technologies or
hardware in the context of robotics projects.

Although primarily focused on robotics applications (taken with its widest acceptation)
some of these contributions can be used in other contexts. Don't hesitate to keep us informed
on any usage you could have made.

Implementation note
-------------------

The collection code is organized using namespace packages, in order to group them in
a single tree rather that resulting in a invading flat collection. Please refer to [this official
documentation](https://www.python.org/dev/peps/pep-0382/) for details.

Package content
===============

This package contains a simple library for communication with Minitels in Python.

In addition to Minitel modes management and interactions, it includes modules for :

    - image hangling :
        - loading from graphics file,
        - converting to Videotex,
        - displaying
    - a simple forms management module, featuring :
        - the ability to store the form definition (prompts, fields,...) as external
          JSON files,
        - data display and entry handling, including special keys for
          navigating, editing and submitting the data.
    - a simple menu management module

It uses elements from :

    - phooky's Minitel : https://github.com/phooky/Minitel
    - zigazou's PyMinitel : https://github.com/Zigazou/PyMinitel/tree/master/minitel

Installation
============

::

    $ python setup.py sdist
    $ pip install dist/*.tar.gz


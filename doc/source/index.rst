
Welcome to PyNitel library documentation!
=========================================

A simple library for communication with Minitels in Python.

In addition to Minitel modes management and interactions, it includes modules for :

    - image hangling :
        - loading from graphics file, 
        - converting to Videotex,
        - displaying 
    - a simple forms management module, featuring :
        - the ability to store the form definition (prompts, fields,...) as external
          JSON files,
        - data display and entry handling, including special keys for
          navigating, editing and submiting the data.

It uses elements from :

    - phooky's Minitel : https://github.com/phooky/Minitel
    - zigazou's PyMinitel : https://github.com/Zigazou/PyMinitel/tree/master/minitel

Contents
--------

.. toctree::
   :maxdepth: 3

   core
   forms
   image
   sequences
   identification
   constants

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


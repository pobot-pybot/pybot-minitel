
Welcome to PyNitel library documentation!
=========================================

A simple library for communication with Minitels in Python.

Based on :

    - phooky's Minitel : https://github.com/phooky/Minitel
    - zigazou's PyMinitel : https://github.com/Zigazou/PyMinitel/tree/master/minitel

I've created my own version because :

    .. rubric:: phooky's one does not work pretty well.

    F.i. the mode switching uses single byte commands, which seem not supported by all the models.
    In addition, the coding style does not respect basic PEP recommendations.

    .. rubric:: zigazou's is very complete, but I dislike its coding style which makes it
       cumbersome to use.

    For instance:

    - it uses a lot of **textual** parameters values instead of predefined constants,
    - there is no convenient way to read data for user input retrieval,...
    - identifiers are in French. Although I **am** French, I can't stand
      French identifiers in code, because it sounds bizarre with English keywords and, more important,
      it makes your code not understandable by non French speakers.

Contents
--------

.. toctree::
   :maxdepth: 3

   core
   forms
   sequences
   identification
   constants

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


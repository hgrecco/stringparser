.. image:: https://img.shields.io/pypi/v/stringparser.svg
    :target: https://pypi.python.org/pypi/stringparser
    :alt: Latest Version

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/python/black

.. image:: https://img.shields.io/pypi/l/stringparser.svg
    :target: https://pypi.python.org/pypi/stringparser
    :alt: License

.. image:: https://img.shields.io/pypi/pyversions/stringparser.svg
    :target: https://pypi.python.org/pypi/stringparser
    :alt: Python Versions

.. image:: https://github.com/hgrecco/stringparser/workflows/CI/badge.svg
    :target: https://github.com/hgrecco/stringparser/actions?query=workflow%3ACI
    :alt: CI

.. image:: https://github.com/hgrecco/stringparser/workflows/Lint/badge.svg
    :target: https://github.com/hgrecco/stringparser/actions?query=workflow%3ALint
    :alt: LINTER

.. image:: https://coveralls.io/repos/github/hgrecco/stringparser/badge.svg?branch=master
    :target: https://coveralls.io/github/hgrecco/stringparser?branch=master
    :alt: Coverage


Motivation
----------

The ``stringparser`` module provides a simple way to match patterns and extract
information within strings. As patterns are given using the familiar format
string specification :pep:`3101`, writing them is much easier than writing
regular expressions (albeit less powerful).

Just install it using:

.. code-block:: bash

   pip install stringparser


Examples
--------

You can build a reusable parser object:

.. code-block:: python

    >>> parser = Parser('The answer is {:d}')
    >>> parser('The answer is 42')
    42
    >>> parser('The answer is 54')
    54

Or directly:

.. code-block:: python

    >>> Parser('The answer is {:d}')('The answer is 42')
    42

You can retrieve many fields:

.. code-block:: python

    >>> Parser('The {:s} is {:d}')('The answer is 42')
    ('answer', 42)

And you can use numbered fields to order the returned tuple:

.. code-block:: python

    >>> Parser('The {1:s} is {0:d}')('The answer is 42')
    (42, 'answer')

Or named fields to return an OrderedDict:

.. code-block:: python

    >>> Parser('The {a:s} is {b:d}')('The answer is 42')
    OrderedDict([('a', 'answer'), ('b', 42)])

You can ignore some fields using _ as a name:

.. code-block:: python

    >>> Parser('The {_:s} is {:d}')('The answer is 42')
    42


Limitations
-----------

- From the format string:
  `[[fill]align][sign][#][0][minimumwidth][.precision][type]`
  only `type`, `sign` and `#` are currently implemented.
  This might cause trouble to match certain notation like:

  - decimal: '-4' written as '-     4'
  - etc

- Lines are matched from beginning to end. {:d} will NOT return all
  the numbers in the string. Use regex for that.

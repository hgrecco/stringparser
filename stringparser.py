#! /usr/bin/env python

# Copyright (c) 2011 Hernan Grecco
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation files
# (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.

"""
Motivation
----------

The ``stringparser`` module provides a simple way to match patterns and extract
information within strings. As patterns are given using the familiar format 
string specification (PEP 3101), writing them is much easier than writing 
regular expressions (albeit less powerful).

Check out the Parser docstring for examples.

Examples
--------

You can build a reusable parser object::

    >>> parser = Parser('The answer is {:d}')
    >>> parser('The answer is 42')
    42

Or directly::

    >>> Parser('The answer is {:d}')('The answer is 42')
    42

You can retrieve many fields::

    >>> Parser('The {:s} is {:d}')('The answer is 42')
    ('answer', 42)

And you can use numbered fields to order the returned tuple::

    >>> Parser('The {1:s} is {0:d}')('The answer is 42')
    (42, 'answer')

Or named fields to return an OrderedDict::

    >>> Parser('The {a:s} is {b:d}')('The answer is 42')
    OrderedDict([('a', 'answer'), ('b', 42)])

You can ignore some fields using _ as a name::

    >>> Parser('The {_:s} is {:d}')('The answer is 42')
    42

Limitations
-----------

- From the format string:
  `[[fill]align][sign][#][0][minimumwidth][.precision][type]`
  only type, sign and # are currently implemented.
  This might cause trouble to match certain notation like:

  - decimal: '-4' written as '-     4'
  - etc

- Lines are matched from beginning to end. {:d} will NOT return all
  the numbers in the string. Use regex for that.
  
"""


__author__ = 'Hernan Grecco <hernan.grecco@gmail.com>'
__license__ = 'MIT <http://www.opensource.org/licenses/mit-license.php>'

__version__ = '0.1'

import re
import sys
import string
if sys.version_info[0] < 3:
    from StringIO import StringIO
else:
    from io import StringIO

from functools import partial

from collections import OrderedDict

_FORMATTER = string.Formatter()

# This dictionary maps each format type to a tuple containing 
#   1. The regular expression to match the string 
#   2. A callable that will used to convert the matched string into the 
#      appropriate Python object.
_REG = {None: ('.*?', str),
        's': ('.*?', str),
        'd': ('[0-9]+?', int),
        'b': ('[0-1]+?', partial(int, base=2)),
        'o': ('[0-7]+?', partial(int, base=8)),
        'x': ('[0-9a-f]+?', partial(int, base=16)),
        'X': ('[0-9A-F]+?', partial(int, base=16)),
        'e': ('[0-9]+\.?[0-9]+(e[-+]?[0-9]+)?', float),
        'E': ('[0-9]+\.?[0-9]+(E[-+]?[0-9]+)?', float),
        'f': ('[0-9]+\.?[0-9]+', float),
        'F': ('[0-9]+\.?[0-9]+', float),
        'g': ('[0-9]+\.?[0-9]+([eE][-+]?[0-9]+)?', float),
        'G': ('[0-9]+\.?[0-9]+([eE][-+]?[0-9]+)?', float),
        '%': ('[0-9]+\.?[0-9]+%', lambda x: float(x[:-1]) / 100)}

# This regex is used to match the parts within standard format specifier string
#
#    [[fill]align][sign][#][0][width][,][.precision][type]
#
#    format_spec ::=  [[fill]align][sign][#][0][width][,][.precision][type]
#    fill        ::=  <a character other than '}'>
#    align       ::=  "<" | ">" | "=" | "^"
#    sign        ::=  "+" | "-" | " "
#    width       ::=  integer
#    precision   ::=  integer
#    type        ::=  "b" | "c" | "d" | "e" | "E" | "f" | "F" | "g" | "G" | "n" | "o" | "s" | "x" | "X" | "%"
_FMT = re.compile("(?P<align>(?P<fill>[^{}])?[<>=\^])?"
                  "(?P<sign>[\+\- ])?(?P<alternate>#)?"
                  "(?P<zero>0)?(?P<width>[0-9]+)?(?P<comma>[,])?"
                  "(?P<precision>\.[0-9]+)?(?P<type>[bcdeEfFgGnosxX%]+)?")


def fmt_to_regex(fmt):
    """ Returns the regex to match and the callable to convert from string  
    or a standard format specifier string.
    """

    (align, fill, sign, alternate, 
     zero, width, comma, precision, ctype) = _FMT.search(fmt).groups()

    try:
        reg, fun = _REG[ctype]
    except KeyError:
        raise ValueError('{} is not an valid type'.format(ctype))

    if alternate:
        if ctype in ('o', 'x', 'X', 'b'):
            reg = '0' + ctype + reg
        else:
            raise ValueError('Alternate form (#) not allowed in {} type'.format(ctype))

    if sign == '-' or sign is None:
        reg = '[-]?' + reg
    elif sign == '+':
        reg = '[-+]' + reg
    elif sign == ' ':
        reg = '[- ]' + reg
    else:
        raise ValueError('{} is not a valid sign'.format(sign))

    return reg, fun


class Parser(object):
    """Callable object to parse a text line using a format string (PEP 3101) 
    as a template.
    """

    def __init__(self, format_string):
        
        # List of tuples (name of the field, converter function)
        self._fields = []

        # If any of the fields has a non-numeric name, this variable is toggled
        # and the return is a dictionary
        self._output_dict = False

        pattern = StringIO()
        max_numeric = 0

        # Assembly regex, list of fields and converter function by inspecting
        # each replacement field.
        for literal, field, fmt, conv in _FORMATTER.parse(format_string):
            pattern.write(re.escape(literal))

            if field is None and fmt is None and conv is None:
                continue

            if fmt is None or fmt == '':
                reg, fun = _REG['s']
            else:
                reg, fun = fmt_to_regex(fmt)

            # Ignored fields are added as non-capturing groups
            # Named and unnamed fields are added as capturing groups
            if field == '_':
                pattern.write('(?:' + reg + ')')
                continue
            elif field == '':
                max_numeric += 1
                field = max_numeric
            else:
                try:
                    field = int(field)
                    max_numeric = field
                except ValueError:
                    self._output_dict = True
            
            pattern.write('(' + reg + ')')
            self._fields.append((field, fun))
        
        self._regex = re.compile('^' + pattern.getvalue() + '$')

    def __call__(self, text):

        # Try to match the text with the stored regex
        mobj = self._regex.match(text)
        if mobj is None:
            raise ValueError("Could not parse "
                             "'{}' with '{}'".format(text, self._regex.pattern))

        # Build a dictionary mapping the field name to the corresponding value
        # converted from string.
        parsed = OrderedDict()
        for group, (field, fun) in zip(mobj.groups(), self._fields):
            if isinstance(field, str) and '.' in field:
                name, prop = field.split('.')
                if not name in parsed:
                    parsed[name] = OrderedDict()
                parsed[field][prop] = fun(group)
            else:
                parsed[field] = fun(group)
        
        # If during parsing, any of the fields was found to have a non-numeric 
        # name, return directly 
        if self._output_dict:
            return parsed

        # If the result contains a single object, return it without Container 
        if len(parsed) == 1:
            return tuple(parsed.values())[0]
        
        # For the rest (multiple fields either unnamed or numbered), 
        # return a tuple 
        return tuple(parsed[key] for key in sorted(parsed.keys()))


if __name__ == '__main__':
    import sys
    if len(sys.argv) != 3:
        print('Usage: stringparser.py pattern string')
        sys.exit(0)
    print(Parser(sys.argv[1])(sys.argv[2]))

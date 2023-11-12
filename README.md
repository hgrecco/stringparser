[![Latest Version](https://img.shields.io/pypi/v/stringparser.svg)](https://pypi.python.org/pypi/stringparser)
[![image](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/python/black)
[![License](https://img.shields.io/pypi/l/stringparser.svg)](https://pypi.python.org/pypi/stringparser)
[![Python Versions](https://img.shields.io/pypi/pyversions/stringparser.svg)](https://pypi.python.org/pypi/stringparser)
[![CI](https://github.com/hgrecco/stringparser/workflows/CI/badge.svg)](https://github.com/hgrecco/stringparser/actions?query=workflow%3ACI)
[![LINTER](https://github.com/hgrecco/stringparser/workflows/Lint/badge.svg)](https://github.com/hgrecco/stringparser/actions?query=workflow%3ALint)
[![Coverage](https://coveralls.io/repos/github/hgrecco/stringparser/badge.svg?branch=master)](https://coveralls.io/github/hgrecco/stringparser?branch=master)

# Motivation

The `stringparser` module provides a simple way to match patterns and
extract information within strings. As patterns are given using the
familiar format string specification [3101](https://peps.python.org/pep-3101/)., writing them is much easier than writing regular
expressions (albeit less powerful).

Just install it using:

```bash
pip install stringparser
```

# Examples

You can build a reusable parser object:

```python
>>> from stringparser import Parser
>>> parser = Parser('The answer is {:d}')
>>> parser('The answer is 42')
42
>>> parser('The answer is 54')
54
```

Or directly:

```python
>>> Parser('The answer is {:d}')('The answer is 42')
42
```

You can retrieve many fields:

```python
>>> Parser('The {:s} is {:d}')('The answer is 42')
['answer', 42]
```

And you can use numbered fields to order the returned list:

```python
>>> Parser('The {1:s} is {0:d}')('The answer is 42')
[42, 'answer']
```

Or named fields to return an OrderedDict:

```python
>>> Parser('The {a:s} is {b:d}')('The answer is 42')
{'a': 'answer', 'b': 42}
```

You can ignore some fields using _ as a name:

```python
>>> Parser('The {_:s} is {:d}')('The answer is 42')
42
```

You can parse into an object attribute:

```python
>>> obj = Parser('The {0.name:s} is {0.value:d}')('The answer is 42')
>>> obj.name
'answer'
>>> obj.value
'42'
```

You can parse even parse into an nested structues:

```python
>>> obj = Parser('The {0.content[name]:s} is {0.content[value]:d}')('The answer is 42')
>>> obj.content
{'name': 'answer', 'value': 42}
```

# Limitations

- From the format string:
  `[[fill]align][sign][#][0][width][,][.precision][type]`
  only `[type]`, `[sign]` and `[#]` are
  currently implemented. This might cause trouble to match certain
  notation like: decimal `-4` written as `- 4`.
- Lines are matched from beginning to end. `{:d}` will NOT return all
  the numbers in the string. Use regex for that.

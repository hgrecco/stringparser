
from setuptools import setup

setup(
	name='stringparser',
    version=0.1,
    description="Easy to use pattern matching and information extraction",
    long_description="""
Motivation
----------

The ``stringparser`` module provides a simple way to match patterns and extract
information within strings. As patterns are given using the familiar format 
string specification (PEP 3101), writing them is much easier than writing 
 regular expressions (albeit less powerful).

Check out the Parser docstring for examples.

Limitations
-----------

- From the format string:
  [[fill]align][sign][#][0][minimumwidth][.precision][type]
  only type is currently implemented.
  This might cause trouble to match certain notation like :
  * decimal: '-4' written as '-     4'
  * boolean: '1' written as 0b1'
  * hex: 'f' written as '0xf'
  * etc

- Lines are matched from beginning to end. {:d} will NOT return all
  the numbers in the string. Use regex for that.
  
""",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.2',
    ],
    author='Hernan Grecco',
    author_email='hernan.grecco@gmail.com',
    url='https://github.com/hgrecco/stringformater',
    license='MIT',
    py_modules=['stringformater'],
    zip_safe=True,
)


from setuptools import setup

from stringparser import __version__, __doc__

setup(
	name='stringparser',
    version=__version__,
    description="Easy to use pattern matching and information extraction",
    long_description=__doc__,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 2.7',
        'Topic :: Text Processing'
    ],
    author='Hernan Grecco',
    author_email='hernan.grecco@gmail.com',
    url='http://github.com/hgrecco/stringparser',
    license='MIT',
    py_modules=['stringformater', ],
    zip_safe=True,
)

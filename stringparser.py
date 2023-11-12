# -*- coding: utf-8 -*-
"""
    stringparser
    ~~~~~~~~~~~~

    A simple way to match patterns and extract information within strings without
    typing regular expressions. It can be considered as the inverse of `format`
    as patterns are given using the familiar format string specification :pep:`3101`.

    :copyright: (c) 2013 by Hernan E. Grecco.
    :license: BSD, see LICENSE for more details.
"""

import copy
import re
import string
from functools import partial
from io import StringIO
from re import (  # noqa: F401
    DOTALL,
    IGNORECASE,
    LOCALE,
    MULTILINE,
    UNICODE,
    VERBOSE,
    I,
    L,
    M,
    S,
    U,
    X,
)
from typing import (
    Any,
    Callable,
    Generator,
    Iterable,
    Literal,
    Optional,
    Union,
    overload,
)

from typing_extensions import TypeAlias


class Dummy:
    """ """

    pass


_FORMATTER = string.Formatter()

# This is due to the fact that int, float, etc
# are not recognized as Callable[[str, ], Any]
STRCALLABLE: TypeAlias = Union[
    type,
    Callable[
        [
            str,
        ],
        Any,
    ],
]

REGEX2CONVERTER: TypeAlias = tuple[str, STRCALLABLE]

# This dictionary maps each format type to a tuple containing
#   1. The regular expression to match the string
#   2. A callable that will used to convert the matched string into the
#      appropriate Python object.

_REG: dict[Optional[str], REGEX2CONVERTER] = {
    None: (".*?", str),
    "s": (".*?", str),
    "d": ("[0-9]+?", int),
    "b": ("[0-1]+?", partial(int, base=2)),
    "o": ("[0-7]+?", partial(int, base=8)),
    "x": ("[0-9a-f]+?", partial(int, base=16)),
    "X": ("[0-9A-F]+?", partial(int, base=16)),
    "e": ("[0-9]+\\.?[0-9]+(?:e[-+]?[0-9]+)?", float),
    "E": ("[0-9]+\\.?[0-9]+(?:E[-+]?[0-9]+)?", float),
    "f": ("[0-9]+\\.?[0-9]+", float),
    "F": ("[0-9]+\\.?[0-9]+", float),
    "g": ("[0-9]+\\.?[0-9]+(?:[eE][-+]?[0-9]+)?", float),
    "G": ("[0-9]+\\.?[0-9]+(?:[eE][-+]?[0-9]+)?", float),
    "%": ("[0-9]+\\.?[0-9]+%", lambda x: float(x[:-1]) / 100),
}

# This regex is used to match the parts within standard format specifier string
#
#    [[fill]align][sign][#][0][width][,][.precision][type]
#
#    fill        ::=  <a character other than '}'>
#    align       ::=  "<" | ">" | "=" | "^"
#    sign        ::=  "+" | "-" | " "
#    width       ::=  integer
#    precision   ::=  integer
#    type        ::=  "b" | "c" | "d" | "e" | "E" | "f" | "F" | "g" | "G" | "n" | "o"
#                     | "s" | "x" | "X" | "%"
_FMT: re.Pattern[str] = re.compile(
    "(?P<align>(?P<fill>[^{}])?[<>=\\^])?"
    "(?P<sign>[\\+\\- ])?(?P<alternate>#)?"
    "(?P<zero>0)?(?P<width>[0-9]+)?(?P<comma>[,])?"
    "(?P<precision>\\.[0-9]+)?(?P<type>[bcdeEfFgGnosxX%]+)?"
)


def fmt_to_regex(fmt: str) -> REGEX2CONVERTER:
    """For a given standard format specifier string it returns
    with the regex to match and the callable to convert from string.

    Not implemented: fill, align, width precision

    :param fmt: format specifier string as defined in :pep:3101
    :type fmt: string
    :return: (regex, converter)
    :rtype: tuple
    """

    matched = _FMT.search(fmt)

    if matched is None:  # pragma: no cover
        raise ValueError(f"Could not parse the formatting string {fmt}")

    (
        _align,
        _fill,
        sign,
        alternate,
        _zero,
        _width,
        _comma,
        _precision,
        ctype,
    ) = matched.groups(default=None)

    try:
        reg, fun = _REG[ctype]  # typing: ignore
    except KeyError:  # pragma: no cover
        raise ValueError("{} is not an valid type".format(ctype))

    if alternate:
        if ctype in ("o", "x", "X", "b"):
            reg = "0" + ctype + reg
        else:  # pragma: no cover
            raise ValueError("Alternate form (#) not allowed in {} type".format(ctype))

    if sign == "-" or sign is None:
        reg = "[-]?" + reg
    elif sign == "+":
        reg = "[-+]" + reg
    elif sign == " ":
        reg = "[- ]" + reg
    else:  # pragma: no cover
        raise ValueError("{} is not a valid sign".format(sign))

    return reg, fun


ITEM_ATTR: TypeAlias = Union[
    tuple[Literal["attribute"], str], tuple[Literal["item"], Any]
]


def split_field_name(name: str) -> Generator[ITEM_ATTR, None, None]:
    """Split a compound field name into multiple simple field names.

    :param name: simple or compound field name
    """

    first = True
    for namepart in name.split("."):
        # Split that part by open bracket chars
        keyparts = namepart.split("[")
        # The first part is just a bare name
        key = keyparts[0]

        # Empty strings are not allowed as field names
        if key == "":  # pragma: no cover
            raise ValueError("empty field name in {}".format(name))

        # The first name in the sequence is used to index
        # the args/kwargs arrays. Subsequent names are used
        # on the result of the previous operation.
        if first:
            first = False
            yield ("item", key)
        else:
            yield ("attribute", key)

        # Now process any bracket expressions which followed
        # the first part.
        for key in keyparts[1:]:
            endbracket = key.find("]")
            if endbracket < 0 or endbracket != len(key) - 1:  # pragma: no cover
                raise ValueError("Invalid field syntax in {}".format(name))

            # Strip off the closing bracket and try to coerce to int
            key = key[:-1]
            try:
                yield ("item", int(key))
            except ValueError:
                yield ("item", key)


def build_hierarchy(field_parts: Iterable[ITEM_ATTR], top: Any) -> Any:
    """Build a hierarchy of dictionary and Dummy object

    :param field_parts: iterable of simple field names and type
    :param top: element to be placed on the top of the hierarchy
    """
    tmp: Union[dict[Any, Any], Dummy]
    for typ, name in reversed(list(field_parts)):
        if typ == "attribute":
            tmp = Dummy()
            setattr(tmp, name, top)
            top = tmp
        elif typ == "item":
            tmp = dict()
            tmp[name] = top
            top = tmp
    return top


def append_to_hierarchy(
    bottom: Any, field_parts: Iterable[ITEM_ATTR], top: Any
) -> None:
    """Append hierarchy to another.

    :param bottom: existing hierarchy
    :param field_parts: iterable of simple field names and type
    :param top: element to be placed on the top of the hierarchy
    """
    for typ_, name in field_parts:
        if isinstance(bottom, dict):
            if not typ_ == "item":  # pragma: no cover
                raise ValueError("Incompatible {}, {}".format(typ_, name))
            try:
                bottom = bottom[name]
            except KeyError:
                bottom[name] = build_hierarchy(field_parts, top)

        elif isinstance(bottom, Dummy):
            if not typ_ == "attribute":  # pragma: no cover
                raise ValueError("Incompatible {}, {}".format(typ_, name))
            try:
                bottom = getattr(bottom, name)
            except AttributeError:  # pragma: no cover
                setattr(bottom, name, build_hierarchy(field_parts, top))
        else:  # pragma: no cover
            raise ValueError("Incompatible {}, {}".format(typ_, name))


def set_in_hierarchy(bottom: Any, field_parts: Iterable[ITEM_ATTR], top: Any) -> None:
    """Traverse a hierarchy and set the top element.

    :param bottom: existing hierarchy
    :param field_parts: iterable of simple field names and type
    :param top: element to be placed on the top of the hierarchy
    """
    for _typ, name in field_parts:
        if isinstance(bottom, dict):
            if bottom[name] is None:
                bottom[name] = top
            else:
                set_in_hierarchy(bottom[name], field_parts, top)
        elif isinstance(bottom, Dummy):
            if getattr(bottom, name) is None:
                setattr(bottom, name, top)
            else:
                set_in_hierarchy(getattr(bottom, name), field_parts, top)
        elif isinstance(bottom, list):
            if bottom[int(name)] is None:
                bottom[int(name)] = top
            else:
                set_in_hierarchy(bottom[int(name)], field_parts, top)


@overload
def convert(obj: None) -> None:
    ...


@overload
def convert(obj: dict[Any, Any]) -> Union[dict[Any, Any], list[Any]]:
    ...


@overload
def convert(obj: Dummy) -> Dummy:
    ...


def convert(obj):
    """Recursively traverse template data structure converting dictionaries
    to lists if all keys are numbers which fill the range from [0, len(keys))

    :param obj: nested template data structure
    """
    if obj is None:
        return None

    elif isinstance(obj, dict):
        try:
            keys = sorted([int(key) for key in obj.keys()])
            if min(keys) == 0 and max(keys) == len(keys) - 1:
                return [convert(obj[str(key)]) for key in keys]
        except Exception:
            pass

        for key, value in obj.items():
            obj[key] = convert(value)
        return obj

    elif isinstance(obj, Dummy):
        for key, value in obj.__dict__.items():
            setattr(obj, key, convert(value))
        return obj


class Parser(object):
    """Callable object to parse a text line using a format string (PEP 3101)
    as a template.

    :param format_string: PEP 3101 format string to be used as a template.
    :param flags: modifies the regex expression behaviour. Passed to re.compile.
    """

    # List of tuples (name of the field, converter function)
    _fields: list[tuple[str, STRCALLABLE]]

    # If any of the fields has a non-numeric name, this variable is toggled
    # and the return is a dictionary
    _output_as_dict: bool

    _template: Union[dict[Any, Any], list[Any], Dummy]

    # Compiled regex pattern
    _regex: re.Pattern[str]

    def __init__(self, format_string: str, flags: Union[re.RegexFlag, int] = 0):
        self._fields = []
        self._output_as_dict = False

        pattern = StringIO()
        number = 0

        # Assembly regex, list of fields, converter function,
        # and output template data structure by inspecting
        # each replacement field.
        template: dict[Any, Any] = dict()
        for literal, field, fmt, _conv in _FORMATTER.parse(format_string):
            pattern.write(re.escape(literal))

            if field is None:
                continue

            if fmt is None or fmt == "":
                reg, fun = _REG["s"]
            else:
                reg, fun = fmt_to_regex(fmt)

            # Ignored fields are added as non-capturing groups
            # Named and unnamed fields are added as capturing groups
            if field == "_":
                pattern.write("(?:" + reg + ")")
                continue

            if not field or field[0] in (".", "["):
                field = str(number) + field
                number += 1

            pattern.write("(" + reg + ")")
            self._fields.append((field, fun))
            append_to_hierarchy(template, split_field_name(field), None)

        self._template = convert(template)
        self._regex = re.compile("^" + pattern.getvalue() + "$", flags)

    def __call__(self, text: str) -> Union[str, list[str], dict[Any, Any], Dummy]:
        # Try to match the text with the stored regex
        mobj = self._regex.search(text)
        if mobj is None:
            raise ValueError(f"Could not parse '{text}' with '{self._regex.pattern}'")

        # Put each matched string in the corresponding output slot in the template
        parsed = copy.deepcopy(self._template)
        for group, (field, fun) in zip(mobj.groups(), self._fields):
            set_in_hierarchy(parsed, split_field_name(field), fun(group))

        # If the result is a list with a single object, return it without Container
        if isinstance(parsed, list) and len(parsed) == 1:
            return parsed[0]

        return parsed

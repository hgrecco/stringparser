import pytest

import stringparser
from stringparser import Parser


class Dummy:
    pass


def _test(fstring, value):
    parser = Parser(fstring)
    text = fstring.format(value)
    assert parser(text) == value


def _test_many(fstring, *value):
    parser = Parser(fstring)
    text = fstring.format(*value)
    for out, val in zip(parser(text), value):
        assert out == val


def _test_dict(fstring, **value):
    parser = Parser(fstring)
    text = fstring.format(**value)
    assert set(parser(text).items()) == set(dict(value).items())


def test_string():
    "Parse single string"
    _test("before {0:s} after", "TEST")


@pytest.mark.xfail
@pytest.mark.parametrize(
    "fstring, value",
    [
        ("{0:x<7s}", "result"),
        ("{0:x<8s}", "result"),
        ("{0: <7s}", "result"),
        ("{0:<7s}", "result"),
        ("{0:>7s}", "result"),
        ("{0:>8s}", "result"),
        ("{0:=8s}", "result"),
        ("{0:^8s}", "result"),
        ("{0:^9s}", "result"),
        ("{0:^10s}", "result"),
    ],
)
def test_string_failure(fstring, value):
    "Unimplemented features for string"
    _test(fstring, value)


def test_escape_re_characters():
    "Escape regex related characters"
    _test("start * | {0:s} [ ( * .after", "TEST")


def test_int():
    "Parse single int"
    _test("before {0:d} after", 42)


@pytest.mark.xfail
@pytest.mark.parametrize(
    "fstring, value",
    [
        ("{0:()d}", -123),
        ("{0:1000d}", 100),
        ("{0:<d}", 1),
        ("{0:>d}", 1),
        ("{0:=d}", 1),
        ("{0:^d}", 1),
        ("{0:<d}", -1),
        ("{0:>d}", -1),
        ("{0:=d}", -1),
        ("{0:^d}", -1),
        ("{0:<10d}", 0),
        ("{0:<10d}", 123),
        ("{0:<10d}", -123),
        ("{0:>10d}", 123),
        ("{0:>10d}", -123),
        ("{0:^10d}", 123),
        ("{0:^10d}", -123),
        ("{0:=10d}", 123),
        ("{0:=+10d}", 123),
        ("{0:=10d}", -123),
        ("{0:=+10d}", -123),
        ("{0:=()10d}", 123),
        ("{0:=()10d}", -123),
        ("{0:>()10d}", -123),
        ("{0:<()10d}", -123),
        ("{0:^()10d}", -123),
        ("{0:d}", 10**100),
        ("{0:d}", -(10**100)),
        ("{0:+d}", 10**100),
        ("{0:()d}", -(10**100)),
        ("{0:()110d}", -(10**100)),
        ("{0:()110d}", -(10**100)),
    ],
)
def test_int_failure(fstring, value):
    "Unimplemented features for int"
    _test(fstring, value)


@pytest.mark.parametrize(
    "fstring, value",
    [
        ("before {0:b} after", 42),
        ("{0:b}", 0),
        ("{0:b}", 42),
        ("{0:b}", -42),
        ("{0:#b}", 42),
        ("{0:#b}", -42),
    ],
)
def test_binary(fstring, value):
    "Parse single binary"


@pytest.mark.xfail
@pytest.mark.parametrize(
    "fstring, value",
    [
        ("{0:<10b}", 0),
        ("{0:>10b}", 0),
        ("{0:<10b}", 9),
        ("{0:>10b}", 9),
        ("{0:^10b}", 9),
        ("{0:()b}", -(2**100 - 1)),
        ("{0:=()200b}", -(2**100 - 1)),
    ],
)
def test_binary_failure(fstring, value):
    _test(fstring, value)


@pytest.mark.parametrize(
    "fstring, value",
    [
        ("before {0:o} after", 42),
        ("before {0:#o} after", 42),
        ("before {0:o} after", -42),
        ("before {0:#o} after", -42),
    ],
)
def test_octal(fstring, value):
    "Parse single octal"
    _test(fstring, value)


@pytest.mark.parametrize(
    "fstring, value",
    [
        ("before {0:x} after", 42),
        ("before {0:X} after", 42),
        ("before {0:#x} after", 42),
        ("before {0:#X} after", 42),
        ("before {0:x} after", -42),
        ("before {0:X} after", -42),
        ("before {0:#x} after", -42),
        ("before {0:#X} after", -42),
    ],
)
def test_hex(fstring, value):
    "Parse single hex (lower and uppercase)"

    _test(fstring, value)


@pytest.mark.parametrize(
    "fstring, value",
    [("before {0:e} after", 42.123e-10), ("before {0:E} after", 42.123e-10)],
)
def test_fp_exp(fstring, value):
    "Parse single floating point exponential format (lower and uppercase)"
    _test(fstring, value)


@pytest.mark.parametrize(
    "fstring, value", [("before {0:f} after", 42.123), ("before {0:F} after", 42.123)]
)
def test_fp_decimal(fstring, value):
    "Parse single Floating point decimal format."

    _test(fstring, value)


@pytest.mark.parametrize(
    "fstring, value",
    [
        ("before {0:g} after", 42.123),
        ("before {0:G} after", 42.123),
        ("before {0:g} after", 42.123e-10),
        ("before {0:G} after", 42.123e-10),
    ],
)
def test_fp_auto(fstring, value):
    """Floating point format. Uses exponential format if exponent is
    greater than -4 or less than precision, decimal format otherwise.
    """
    _test(fstring, value)


def test_percent():
    "Parse single percent"
    _test("before {0:%} after", 42)


def test_unnamed():
    _test("before {:d} after", 42)


def test_named():
    _test_dict("before {a:d} after", a=42)
    _test_dict("before {a:d} in between {b:d} after", a=42, b=23)


@pytest.mark.xfail
def test_attributes():
    h = Dummy()
    h.first = "something"
    h.seccond = "else"

    fmt = "before {0.first} after"
    text = fmt.format(h)
    obj = Parser(fmt)(text)
    assert obj.first == h.first

    fmt = "before {0.first} in between {0.second} after"
    text = fmt.format(h)
    obj = Parser(fmt)(text)
    assert obj.first == h.first
    assert obj.second == h.second

    fmt = "before {0.first} in between {1.second} after"
    text = fmt.format(h)
    obj1, obj2 = Parser(fmt)(text)
    assert obj1.first == h.first
    assert obj2.second == h.second


def test_items():
    h = dict()
    h["first"] = "something"
    h["second"] = "else"

    fmt = "before {0[first]} after"
    text = fmt.format(h)
    obj = Parser(fmt)(text)
    assert obj["first"] == h["first"]

    fmt = "before {0[first]} in between {0[second]} after"
    text = fmt.format(h)
    obj = Parser(fmt)(text)
    assert obj["first"] == h["first"]
    assert obj["second"] == h["second"]

    fmt = "before {0[first]} in between {1[second]} after"
    text = fmt.format(h, h)
    obj1, obj2 = Parser(fmt)(text)
    assert obj1["first"] == h["first"]
    assert obj2["second"] == h["second"]


def test_items_attributes():
    h = Dummy()
    h.first = {"second": "something"}

    fmt = "before {0.first[second]} after"
    text = fmt.format(h)
    obj = Parser(fmt)(text)
    assert obj.first["second"] == h.first["second"]

    h = {"first": Dummy()}
    h["first"].second = "something"
    fmt = "before {0[first].second} after"
    text = fmt.format(h)
    obj = Parser(fmt)(text)
    assert obj["first"].second == h["first"].second


def test_object_items():
    h = dict()
    h["aprop"] = "middle"
    h["aprop2"] = "second"

    fmt = "before {0[aprop]} after"
    text = fmt.format(h)
    obj = Parser(fmt)(text)
    assert obj["aprop"] == h["aprop"]

    fmt = "before {0[aprop]} in between {0[aprop2]} after"
    text = fmt.format(h)
    obj = Parser(fmt)(text)
    assert obj["aprop"] == h["aprop"]
    assert obj["aprop2"] == h["aprop2"]

    fmt = "before {0[aprop]} in between {1[aprop2]} after"
    text = fmt.format(h, h)
    obj1, obj2 = Parser(fmt)(text)
    assert obj1["aprop"] == h["aprop"]
    assert obj2["aprop2"] == h["aprop2"]


def test_many_numbered():
    "Parse many numbered"
    _test_many("before {0:d} after {1:d} end", 42, 43)


def test_many_named():
    "Parse many named"
    _test_dict("before {a:d} after {b:d} end", a=42, b=23)


def test_many_scientific():
    "Parse many scientific notation floats"
    for format in "eEgG":
        _test_many(
            "before {0:" + format + "} after {1:" + format + "} end",
            42.123e-10,
            78.532e25,
        )


def test_many_unnamed():
    "Parse many unnamed"
    _test_many("before {:d} after {:d} end", 42, 43)


def test_ignore():
    "Parse single"
    parser = Parser("before {_:d} after")
    assert parser("before 42 after") == dict()


def test_fail():
    "Parse fail"
    parser = Parser("before {:d} after")
    with pytest.raises(ValueError):
        parser("before bla after")


def test_multiline():
    "Test multipline"
    parser = Parser("before {:d} after", stringparser.MULTILINE)
    assert parser("bla\nbefore 42 after\nbla") == 42

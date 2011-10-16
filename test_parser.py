import unittest

from collections import OrderedDict

from stringparser import Parser

class ParserTest(unittest.TestCase):

    def _test(self, fstring, value):
        parser = Parser(fstring)
        text = fstring.format(value)
        self.assertEqual(parser(text), value)

    def _test_many(self, fstring, *value):
        parser = Parser(fstring)
        text = fstring.format(*value)
        for out, val in zip(parser(text), value):
            self.assertEqual(out, val)

    def _test_dict(self, fstring, **value):
        parser = Parser(fstring)
        text = fstring.format(**value)
        self.assertEqual(parser(text), OrderedDict(value))

    def test_single_string(self):
        "Parse single string"
        self._test('before {0:s} after', 'TEST')

    def test_escape_re_characters(self):
        "Parse single string"
        self._test('before * | {0:s} [ ( * .after', 'TEST')

    def test_single_int(self):
        "Parse single int"
        self._test('before {0:d} after', 42)

    def test_single_binary(self):
        "Parse single binary"
        self._test('before {0:b} after', 42)
        self._test("{0:b}", 0)
        self._test("{0:b}", 42)
        self._test("{0:b}", -42)

        self._test("{0:#b}", 42)
        self._test("{0:#b}", -42)

    @unittest.expectedFailure
    def test_binary_failure(self):
        self._test("{0:<10b}", 0)
        self._test("{0:>10b}", 0)
        self._test("{0:<10b}", 9)
        self._test("{0:>10b}", 9)
        self._test("{0:^10b}", 9)

        self._test("{0:()b}", -(2**100 - 1))
        self._test("{0:=()200b}", -(2**100 - 1))

    def test_single_octal(self):
        "Parse single octal"
        self._test('before {0:o} after', 42)
        self._test('before {0:#o} after', 42)

    def test_single_hex(self):
        "Parse single hex (lower and uppercase)"
        self._test('before {0:x} after', 42)
        self._test('before {0:X} after', 42)

        self._test('before {0:#x} after', 42)
        self._test('before {0:#X} after', 42)

    def test_single_fp_exp(self):
        "Parse single floating point exponential format (lower and uppercase)"
        self._test('before {0:e} after', 42.123e-10)
        self._test('before {0:E} after', 42.123e-10)

    def test_single_fp_decimal(self):
        "Parse single Floating point decimal format."
        self._test('before {0:f} after', 42.123)
        self._test('before {0:F} after', 42.123)

    def test_single_fp_auto(self):
        """Floating point format. Uses exponential format if exponent is
        greater than -4 or less than precision, decimal format otherwise.
        """
        self._test('before {0:g} after', 42.123)
        self._test('before {0:G} after', 42.123)
        self._test('before {0:g} after', 42.123e-10)
        self._test('before {0:G} after', 42.123e-10)

    def test_single_percent(self):
        "Parse single percent"
        self._test('before {0:%} after', 42)

    def test_single_unnamed(self):
        self._test('before {:d} after', 42)

    def test_single_named(self):
        self._test_dict('before {a:d} after', a=42)

    def test_many_numbered(self):
        "Parse many numbered"
        self._test_many('before {0:d} after {1:d} end', 42, 43)

    def test_many_named(self):
        "Parse many named"
        self._test_dict('before {a:d} after {b:d} end', a=42, b=43)

    def test_many_unnamed(self):
        "Parse many unnamed"
        self._test_many('before {:d} after {:d} end', 42, 43)

    def test_single_ignore(self):
        "Parse single"
        parser = Parser('before {_:d} after')
        self.assertEqual(parser('before 42 after'), ())

    def test_fail(self):
        "Parse fail"
        parser = Parser('before {:d} after')
        self.assertRaises(ValueError, parser, 'before bla after')

    def test_just_string(self):
        "Parse single string"
        self._test('{0:s}', 'TEST')

if __name__ == '__main__':
    unittest.main()

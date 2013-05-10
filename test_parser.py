import unittest

from collections import OrderedDict

import stringparser

from stringparser import Parser

class Dummy():
    pass


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

    def test_string(self):
        "Parse single string"
        self._test('before {0:s} after', 'TEST')

    @unittest.expectedFailure
    def test_string_failure(self):
        "Unimplemented features for string"
        self._test("{0:x<7s}", "result")
        self._test("{0:x<8s}", "result")
        self._test("{0: <7s}", "result")
        self._test("{0:<7s}", "result")
        self._test("{0:>7s}", "result")
        self._test("{0:>8s}", "result")
        self._test("{0:=8s}", "result")
        self._test("{0:^8s}", "result")
        self._test("{0:^9s}", "result")
        self._test("{0:^10s}", "result")

    def test_escape_re_characters(self):
        "Escape regex related characters"
        self._test('start * | {0:s} [ ( * .after', 'TEST')

    def test_int(self):
        "Parse single int"
        self._test('before {0:d} after', 42)

    @unittest.expectedFailure
    def test_int_failure(self):
        "Unimplemented features for int"
        self._test("{0:()d}", -123)

        self._test("{0:1000d}", 100)

        self._test("{0:<d}", 1)
        self._test("{0:>d}", 1)
        self._test("{0:=d}", 1)
        self._test("{0:^d}", 1)
        self._test("{0:<d}", -1)
        self._test("{0:>d}", -1)
        self._test("{0:=d}", -1)
        self._test("{0:^d}", -1)

        self._test("{0:<10d}", 0)
        self._test("{0:<10d}", 123)
        self._test("{0:<10d}", -123)
        self._test("{0:>10d}", 123)
        self._test("{0:>10d}", -123)
        self._test("{0:^10d}", 123)
        self._test("{0:^10d}", -123)
        self._test("{0:=10d}", 123)
        self._test("{0:=+10d}", 123)
        self._test("{0:=10d}", -123)
        self._test("{0:=+10d}", -123)
        self._test("{0:=()10d}", 123)

        self._test("{0:=()10d}", -123)
        self._test("{0:>()10d}", -123)
        self._test("{0:<()10d}", -123)
        self._test("{0:^()10d}", -123)

        self._test("{0:d}", 10**100)
        self._test("{0:d}", -10**100)
        self._test("{0:+d}", 10**100)
        self._test("{0:()d}", -10**100)
        self._test("{0:()110d}", -10**100)
        self._test("{0:()110d}", -10**100)

    def test_binary(self):
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

    def test_octal(self):
        "Parse single octal"
        self._test('before {0:o} after', 42)
        self._test('before {0:#o} after', 42)
        self._test('before {0:o} after', -42)
        self._test('before {0:#o} after', -42)

    def test_hex(self):
        "Parse single hex (lower and uppercase)"
        self._test('before {0:x} after', 42)
        self._test('before {0:X} after', 42)

        self._test('before {0:#x} after', 42)
        self._test('before {0:#X} after', 42)

        self._test('before {0:x} after', -42)
        self._test('before {0:X} after', -42)

        self._test('before {0:#x} after', -42)
        self._test('before {0:#X} after', -42)

    def test_fp_exp(self):
        "Parse single floating point exponential format (lower and uppercase)"
        self._test('before {0:e} after', 42.123e-10)
        self._test('before {0:E} after', 42.123e-10)

    def test_fp_decimal(self):
        "Parse single Floating point decimal format."
        self._test('before {0:f} after', 42.123)
        self._test('before {0:F} after', 42.123)

    def test_fp_auto(self):
        """Floating point format. Uses exponential format if exponent is
        greater than -4 or less than precision, decimal format otherwise.
        """
        self._test('before {0:g} after', 42.123)
        self._test('before {0:G} after', 42.123)
        self._test('before {0:g} after', 42.123e-10)
        self._test('before {0:G} after', 42.123e-10)

    def test_percent(self):
        "Parse single percent"
        self._test('before {0:%} after', 42)

    def test_unnamed(self):
        self._test('before {:d} after', 42)

    def test_named(self):
        self._test_dict('before {a:d} after', a=42)
        self._test_dict('before {a:d} in between {b:d} after', a=42, b=23)

    @unittest.expectedFailure
    def test_attributes(self):
        h = Dummy()
        h.first = 'something'
        h.seccond = 'else'

        fmt = 'before {0.first} after'
        text = fmt.format(h)       
        obj = Parser(fmt)(text)
        self.assertEqual(obj.first, h.first)

        fmt = 'before {0.first} in between {0.second} after'
        text = fmt.format(h)
        obj = Parser(fmt)(text)
        self.assertEqual(obj.first, h.first)
        self.assertEqual(obj.second, h.second)

        fmt = 'before {0.first} in between {1.second} after'
        text = fmt.format(h)
        obj1, obj2 = Parser(fmt)(text)
        self.assertEqual(obj1.first, h.first)
        self.assertEqual(obj2.second, h.second)        


    def test_items(self):
        h = dict()
        h['first'] = 'something'
        h['second'] = 'else'

        fmt = 'before {0[first]} after'
        text = fmt.format(h)       
        obj = Parser(fmt)(text)
        self.assertEqual(obj['first'], h['first'])

        fmt = 'before {0[first]} in between {0[second]} after'
        text = fmt.format(h)
        obj = Parser(fmt)(text)
        self.assertEqual(obj['first'], h['first'])
        self.assertEqual(obj['second'], h['second'])

        fmt = 'before {0[first]} in between {1[second]} after'
        text = fmt.format(h, h)
        obj1, obj2 = Parser(fmt)(text)
        self.assertEqual(obj1['first'], h['first'])
        self.assertEqual(obj2['second'], h['second'])        

    def test_items_attributes(self):
        h = Dummy()
        h.first = {'second': 'something'}

        fmt = 'before {0.first[second]} after'
        text = fmt.format(h)       
        obj = Parser(fmt)(text)
        self.assertEqual(obj.first['second'], h.first['second'])

        h = {'first': Dummy()}
        h['first'].second = 'something'
        fmt = 'before {0[first].second} after'
        text = fmt.format(h)
        obj = Parser(fmt)(text)
        self.assertEqual(obj['first'].second, h['first'].second)
     

    def test_object_items(self):
        h = dict()
        h['aprop'] = 'middle'
        h['aprop2'] = 'second'

        fmt = 'before {0[aprop]} after'
        text = fmt.format(h)       
        obj = Parser(fmt)(text)
        self.assertEqual(obj['aprop'], h['aprop'])

        fmt = 'before {0[aprop]} in between {0[aprop2]} after'
        text = fmt.format(h)
        obj = Parser(fmt)(text)
        self.assertEqual(obj['aprop'], h['aprop'])
        self.assertEqual(obj['aprop2'], h['aprop2'])

        fmt = 'before {0[aprop]} in between {1[aprop2]} after'
        text = fmt.format(h, h)
        obj1, obj2 = Parser(fmt)(text)
        self.assertEqual(obj1['aprop'], h['aprop'])
        self.assertEqual(obj2['aprop2'], h['aprop2'])      


    def test_many_numbered(self):
        "Parse many numbered"
        self._test_many('before {0:d} after {1:d} end', 42, 43)

    def test_many_named(self):
        "Parse many named"
        self._test_dict('before {a:d} after {b:d} end', a=42, b=43)

    def test_many_scientific(self):
        "Parse many scientific notation floats"
        for format in 'eEgG':
            self._test_many('before {0:'+format+'} after {1:'+format+'} end', 42.123e-10, 78.532e+25)

    def test_many_unnamed(self):
        "Parse many unnamed"
        self._test_many('before {:d} after {:d} end', 42, 43)

    def test_ignore(self):
        "Parse single"
        parser = Parser('before {_:d} after')
        self.assertEqual(parser('before 42 after'), OrderedDict())

    def test_fail(self):
        "Parse fail"
        parser = Parser('before {:d} after')
        self.assertRaises(ValueError, parser, 'before bla after')

    def test_multiline(self):
        "Test multipline"
        parser = Parser('before {:d} after', stringparser.MULTILINE)
        self.assertEqual(parser('bla\nbefore 42 after\nbla'), 42)

if __name__ == '__main__':
    unittest.main()

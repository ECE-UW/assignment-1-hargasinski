## A simple unit test example. Replace by your own tests

import re
import sys
import unittest

import a1ece650 as a1

class MyTest(unittest.TestCase):

    def test_parse_valid_add(self):
        """Test the parser functionality for valid add commands"""
        add_result = a1.parse('a "Weber Street" (1,1) (2,-2)')
        add_expected = {
            'command': 'a',
            'street_name': 'Weber Street',
            'coordinates': [(1,1),(2,-2)]
        }
        self.assertDictEqual(add_result, add_expected)

        add_neg_result = a1.parse('a "NoSpace" (-1,-2)(-3,-4)')
        add_neg_expected = {
            'command': 'a',
            'street_name': 'NoSpace',
            'coordinates': [(-1,-2),(-3,-4)]
        }
        self.assertDictEqual(add_neg_result, add_neg_expected)

    def test_parse_valid_remove(self):
        """Test the parser functionality for valid input"""
        remove_result = a1.parse('r "Weber Street"')
        remove_expected = {
            'command': 'r',
            'street_name': 'Weber Street',
            'coordinates': []
        }
        self.assertDictEqual(remove_result, remove_expected)

    def test_isupper(self):
        """Test isupper() function of class string"""
        self.assertTrue('FOO'.isupper())
        self.assertFalse('foo'.isupper())
        self.assertFalse('foo'.isupper())
        self.assertFalse('Foo'.isupper())

    def test_failing(self):
        """A test that fails"""
        self.assertEqual(True, False)

if __name__ == '__main__':
    unittest.main()

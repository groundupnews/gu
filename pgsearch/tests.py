from django.test import TestCase
from .utils import parseSearchString

class TextSearch(TestCase):

    def test_search_strings(self):
        s = 'The quick, "brown fox, jumps" over the lazy dog.'
        result = parseSearchString(s)
        comparator = ['The', 'quick', 'brown fox jumps',
                      'over', 'the', 'lazy', 'dog']
        self.assertEqual(result, comparator)

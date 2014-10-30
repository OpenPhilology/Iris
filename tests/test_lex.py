# -*- coding: utf-8 -*-
import unittest
import os
import tempfile
from iris import lex

class DictTests(unittest.TestCase):
    """
    General tests for the dict.py module.
    """

    def setUp(self):
        self.temp = tempfile.NamedTemporaryFile()
        self.temp.write(u'word1\n'.encode(u'utf-8'))
        self.temp.write(u'word2\n'.encode(u'utf-8'))
        self.temp.write(u'αχιλλεύς\n'.encode(u'utf-8')) #Achilles, in NFD
        self.temp.write(u'αχιλλεύς\n'.encode(u'utf-8')) #Achilles, in NFD
        self.temp.seek(0, 0)
        self.path = os.path.abspath(self.temp.name)

    def tearDown(self):
        self.temp.close()

    def test_cleanlines(self):
        """
        Test the cleanline function.
        """
        words = lex.cleanlines(self.path)
        self.assertEqual(len(words), 4)
        self.assertEqual(words[0], u'word1')
        self.assertEqual(words[1], u'word2')
        self.assertEqual(words[2], u'αχιλλεύς')
        self.assertEqual(words[3], u'αχιλλεύς')



if __name__ == '__main__':
    unittest.main()
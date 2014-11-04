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

    def test_cleanwords(self):
        """
        Test the cleanwords function.
        """
        self.temp.write(u'adding a line with multiple words\n'.encode(u'utf-8'))
        self.temp.write(u'another with Greek αχιλλεύς\n'.encode(u'utf-8'))
        self.temp.write(u'and some NFC αχιλλεύς\n'.encode(u'utf-8'))
        self.temp.seek(0, 0)
        expected = [u'adding', u'a', u'line', u'with', u'multiple', u'words',
                    u'another', u'with',  u'Greek', u'αχιλλεύς', u'and',
                    u'some', u'NFC', u'αχιλλεύς']
        words = lex.cleanwords(self.path)
        self.assertEqual(words, expected)

    def test_cleanuniquewords(self):
        """
        Test the cleanuniquewords function.
        """
        self.temp1 = tempfile.NamedTemporaryFile()
        self.temp1.write(u'adding a line with multiple words\n'.encode(u'utf-8'))
        self.temp1.write(u'another with Greek αχιλλεύς\n'.encode(u'utf-8'))
        self.temp1.write(u'and some NFC αχιλλεύς\n'.encode(u'utf-8'))
        self.temp1.seek(0, 0)
        expected = set([u'adding', u'a', u'line', u'with', u'multiple', u'words',
                    u'another', u'with',  u'Greek', u'αχιλλεύς', u'and',
                    u'some', u'NFC', u'αχιλλεύς'])
        self.assertEqual(lex.cleanuniquewords(self.temp1.name), expected)

    def test_words_from_files(self):
        """
        Test the words_from_files function.
        """
        dirpath = tempfile.mkdtemp()
        self.temp1 = tempfile.NamedTemporaryFile(dir=dirpath)
        self.temp2 = tempfile.NamedTemporaryFile(dir=dirpath)
        self.temp3 = tempfile.NamedTemporaryFile(dir=dirpath)
        self.dirtofilter = tempfile.mkdtemp(dir=dirpath) #To be filtered out
        self.temp1.write(u'a')
        self.temp2.write(u'b')
        self.temp3.write(u'c')
        self.temp1.seek(0, 0)
        self.temp2.seek(0, 0)
        self.temp3.seek(0, 0)
        words = lex.words_from_files(dirpath)
        self.assertEqual(3, len(words))
        self.assertTrue(u'a' in words)
        self.assertTrue(u'b' in words)
        self.assertTrue(u'c' in words)

    def test_unique_words_from_files(self):
        """
        Test the words_from_files_function.
        """
        dirpath = tempfile.mkdtemp()
        self.temp1 = tempfile.NamedTemporaryFile(dir=dirpath)
        self.temp2 = tempfile.NamedTemporaryFile(dir=dirpath)
        self.temp3 = tempfile.NamedTemporaryFile(dir=dirpath)
        self.temp4 = tempfile.NamedTemporaryFile(dir=dirpath)
        self.dirtofilter = tempfile.mkdtemp(dir=dirpath) #To be filtered out
        self.temp1.write(u'a')
        self.temp2.write(u'b b')
        self.temp3.write(u'c a')
        self.temp4.write(u'a b c \nd')
        self.temp1.seek(0, 0)
        self.temp2.seek(0, 0)
        self.temp3.seek(0, 0)
        self.temp4.seek(0, 0)
        words = lex.unique_words_from_files(dirpath)
        self.assertEqual(4, len(words))
        self.assertTrue(u'a' in words)
        self.assertTrue(u'b' in words)
        self.assertTrue(u'c' in words)        
        self.assertTrue(u'd' in words)        



if __name__ == '__main__':
    unittest.main()
# -*- coding: utf-8 -*-
import unittest
import re
import tempfile

from lxml import etree
from iris import hocr

class HocrTests(unittest.TestCase):
    """
    Tests algorithms dealing with hocr manipulation.
    """

    def setUp(self):
        self.maxDiff = None
        self.temp = tempfile.NamedTemporaryFile()

    def tearDown(self):
        self.temp.close()

    def test_simple_word_extract(self):
        self.temp.write("""<html><body><span class='ocrx_word' id='word_10' title="bbox 260 196 305 232">εἰς</span></body><html>""")
        self.temp.seek(0,0)
        for t in hocr.extract_hocr_tokens(self.temp):
            self.assertEqual('εἰς'.decode('utf-8'), t)

    def test_bbox_extract_simple(self):
        """"
        Test hocr bbox extraction in some simple cases.
        """
        self.temp.write(u'<root title="bbox 1 2 3 4"></root>')
        self.temp.seek(0,0)
        bboxes = hocr.extract_bboxes(self.temp)
        self.assertEqual([(1, 2, 3, 4)], bboxes[hocr.ALL_BBOXES])

    def test_bbox_extract_complex(self):
        """
        Test hocr bbox extraction on a larger document.
        """
        self.temp.write(u"""<root>
                         <p title="text before bbox 1 2 3 4"></p>
                         <p title="bbox 5 6 7 8textafter"></p>
                         <p title="textbeforebbox 9 10 11 12textafter"></p>
                         </root>""")
        self.temp.seek(0,0)

        bboxes = hocr.extract_bboxes(self.temp)
        self.assertEqual([(1, 2, 3, 4), (5, 6, 7, 8), (9, 10, 11, 12)],
                         bboxes[u'//*[@title]'])

    def test_bbox_extract_by_name(self):
        """
        Extract a single class of bboxes.
        """
        xml = u"""<root>
                <p class="c1" title="text before bbox 1 2 3 4"></p>
                <p class="c1" title="bbox 5 6 7 8textafter"></p>
                <p class="c1" title="textbeforebbox 9 10 11 12textafter"></p>
                </root>"""
        self.temp.write(xml)
        self.temp.seek(0,0)
        expected = {u"//*[@class='c1' and @title]":[(1,2,3,4),(5,6,7,8),(9,10,11,12)]}
        self.assertEqual(expected, hocr.extract_bboxes(self.temp, [u"//*[@class='c1' and @title]"]))

    def test_bbox_extract_by_name_multi(self):
        """
        Extract multiple classes of bboxes, while ignoring others.
        """
        xml = u"""<root>
                <p class="c1" title="text before bbox 1 2 3 4"></p>
                <p class="c2" title="bbox 5 6 7 8textafter"></p>
                <p class="c3" title="textbeforebbox 9 10 11 12textafter"></p>
                <p class="whatever" title="13 14 15 16"></p>
                <p class="more whatever" title="17 18 19 20"></p>
                </root>"""
        self.temp.write(xml)
        self.temp.seek(0,0)
        expected = {u"//*[@class='c1' and @title]":[(1,2,3,4)],
                    u"//*[@class='c2' and @title]":[(5,6,7,8)],
                    u"//*[@class='c3' and @title]":[(9,10,11,12)]}
        actual = hocr.extract_bboxes(self.temp, [u"//*[@class='c1' and @title]",
                                                          u"//*[@class='c2' and @title]",
                                                          u"//*[@class='c3' and @title]"])
        self.assertEqual(expected, actual)

    def test_extract_suggestions(self):
        """
        Test the extract_suggestions function.
        """
        xml = u"""
                <root>
                  <span class='ocr_word' id='some_word' title='bbox 1 2 3 4'>
                    <span class="alternatives">
                      <ins class="alt" title="nlp 0.9">already_exists</ins>
                      <ins class="alt" title="nlp 0.8">also_already_exists</ins>
                    </span>
                  </span>
                </root>
                """
        self.temp.write(xml)
        self.temp.seek(0,0)
        with hocr.HocrContext(self.temp.name) as con:
            onlyword, xpath = hocr.extract_words(con)[0]

            self.assertEqual([(u'already_exists', 0.9), (u'also_already_exists', 0.8)], hocr.extract_suggestions(con, xpath))


    def test_insert_suggestions(self):
        """
        Test the insert_suggestions function.
        """
        xml = u"""
                <root>
                <span class='ocr_word' id='some_word' title='bbox 1 2 3 4'>theword</span>
                </root>
                """
        self.temp.write(xml)
        self.temp.seek(0,0)
        with hocr.HocrContext(self.temp.name) as con:
            onlyword, xpath = hocr.extract_words(con)[0]
            suggestions = [(u'foo', 0.1), (u'bar', 0.2), (u'qux', 0.3), (u'lol', 0.4)]
            hocr.insert_suggestions(con, xpath, suggestions)

            self.assertEqual(suggestions, hocr.extract_suggestions(con, xpath))

    def test_insert_suggestions_preexisting(self):
        """
        Test the insert_suggestions function.
        """
        xml = u"""
                <root>
                  <span class='ocr_word' id='some_word' title='bbox 1 2 3 4'>
                    <span class="alternatives">
                      <ins class="alt" title="nlp 0.9">already_exists</ins>
                      <ins class="alt" title="nlp 0.8">also_already_exists</ins>
                    </span>
                  </span>
                </root>
                """
        self.temp.write(xml)
        self.temp.seek(0,0)
        with hocr.HocrContext(self.temp.name) as con:
            onlyword, xpath = hocr.extract_words(con)[0]
            suggestions = [(u'foo', 0.1), (u'bar', 0.2), (u'qux', 0.3), (u'lol', 0.4)]
            hocr.insert_suggestions(con, xpath, suggestions)

            expected = [(u'already_exists', 0.9), (u'also_already_exists', 0.8),
                                                  (u'foo', 0.1), (u'bar', 0.2),
                                                  (u'qux', 0.3), (u'lol', 0.4)]
            self.assertEqual(expected, hocr.extract_suggestions(con, xpath))


    def test_insert_suggestion(self):
        """
        Test the insert_suggestion function.
        """
        xml = u"""
                <root>
                <span class='ocr_word' id='some_word' title='bbox 1 2 3 4'>theword</span>
                </root>
                """
        self.temp.write(xml)
        self.temp.seek(0,0)
        with hocr.HocrContext(self.temp.name) as con:
            onlyword, xpath = hocr.extract_words(con)[0]
            hocr.insert_suggestion(con, xpath, u'foobar', 0.5)


    def test_unchecked_words_xpath(self):
        xml = u"""
                <root>
                  <span class='ocr_word' id='some_word' title='bbox 1 2 3 4'>word</span>
                  <span class='ocr_word' id='some_word' title='bbox 1 2 3 4'><p>something</p></span>
                  <span class='ocrx_word' id='some_word' title='bbox 1 2 3 4'>word</span>
                  <span class='ocrx_word' id='some_word' title='bbox 1 2 3 4'><p>something</p></span>
                </root>
                """
        self.temp.write(xml)
        self.temp.seek(0,0)
        with hocr.HocrContext(self.temp.name) as con:
            spans = hocr.extract_words(con)
            self.assertEqual(u'word', con.xpath(hocr.UNCHECKED_WORDS)[0].text)
            self.assertEqual(u'word', con.xpath(hocr.UNCHECKED_XWORDS)[0].text)

    def test_check_hocr_all(self):
        """
        Test the spellcheck hocr function with xpath that will
        correct all words in the document.
        """
        xml = u"""
               <root>
                 <span class='ocr_word' id='some_word' title='bbox 1 2 3 4'>aaa</span>
                 <span class='ocr_word' id='some_word' title='bbox 1 2 3 4'>bbb</span>
                 <span class='ocr_word' id='some_word' title='bbox 1 2 3 4'>ccc</span>
               </root>
               """
        self.temp.write(xml)
        self.temp.seek(0,0)
        dic = {u'aaaa', u'bbbb', u'cccc'}
        del_dic = tempfile.NamedTemporaryFile()
        del_dic.write(u'aaa\taaaa\n')
        del_dic.write(u'bbb\tbbbb\n')
        del_dic.write(u'ccc\tcccc\n')
        del_dic.seek(0,0)
        expected = u"""
                    <root>
                      <span class='ocr_word' id='some_word' title='bbox 1 2 3 4'>
                        <span class="alternatives">
                          <ins class="alt" title="nlp 0.9">aaaa</ins>
                        </span>
                      </span>
                      <span class='ocr_word' id='some_word' title='bbox 1 2 3 4'>
                        <span class="alternatives">
                          <ins class="alt" title="nlp 0.9">bbbb</ins>
                        </span>
                      </span>
                      <span class='ocr_word' id='some_word' title='bbox 1 2 3 4'>
                        <span class="alternatives">
                          <ins class="alt" title="nlp 0.9">cccc</ins>
                        </span>
                      </span>
                    </root>
                    """
        with hocr.HocrContext(self.temp.name) as con:
            hocr.spellcheck_hocr(con, hocr.UNCHECKED_WORDS, dic, del_dic.name.decode(u'utf-8'), 1)
            actual_string = etree.tostring(con.getroot(), pretty_print=True).replace(u'\n', u'').replace(u'\t', u'').replace(u' ', u'')
            expected_string = etree.tostring(etree.XML(expected), pretty_print=True).replace(u'\n', u'').replace(u'\t', u'').replace(u' ', u'')
            print actual_string
            print expected_string
            self.assertEqual(expected_string, actual_string)

    def test_check_hocr_with_filedict_all(self):
        """
        Test the spellcheck hocr function with xpath that will
        correct all words in the document.
        """
        xml = u"""
               <root>
                 <span class='ocr_word' id='some_word' title='bbox 1 2 3 4'>aaa</span>
                 <span class='ocr_word' id='some_word' title='bbox 1 2 3 4'>bbb</span>
                 <span class='ocr_word' id='some_word' title='bbox 1 2 3 4'>ccc</span>
               </root>
               """
        self.temp.write(xml)
        self.temp.seek(0,0)
        dic = tempfile.NamedTemporaryFile()
        dic.write(u'aaaa\n')
        dic.write(u'bbbb\n')
        dic.write(u'cccc\n')
        dic.seek(0,0)
        del_dic = tempfile.NamedTemporaryFile()
        del_dic.write(u'aaa\taaaa\n')
        del_dic.write(u'bbb\tbbbb\n')
        del_dic.write(u'ccc\tcccc\n')
        del_dic.seek(0,0)
        expected = u"""
                    <root>
                      <span class='ocr_word' id='some_word' title='bbox 1 2 3 4'>
                        <span class="alternatives">
                          <ins class="alt" title="nlp 0.9">aaaa</ins>
                        </span>
                      </span>
                      <span class='ocr_word' id='some_word' title='bbox 1 2 3 4'>
                        <span class="alternatives">
                          <ins class="alt" title="nlp 0.9">bbbb</ins>
                        </span>
                      </span>
                      <span class='ocr_word' id='some_word' title='bbox 1 2 3 4'>
                        <span class="alternatives">
                          <ins class="alt" title="nlp 0.9">cccc</ins>
                        </span>
                      </span>
                    </root>
                    """
        with hocr.HocrContext(self.temp.name) as con:
            hocr.spellcheck_hocr_with_filedict(con, hocr.UNCHECKED_WORDS, dic.name.decode(u'utf-8'), del_dic.name.decode(u'utf-8'), 1)
            actual_string = etree.tostring(con.getroot(), pretty_print=True).replace(u'\n', u'').replace(u'\t', u'').replace(u' ', u'')
            expected_string = etree.tostring(etree.XML(expected), pretty_print=True).replace(u'\n', u'').replace(u'\t', u'').replace(u' ', u'')
            print actual_string
            print expected_string
            self.assertEqual(expected_string, actual_string)




if __name__ == '__main__':
    unittest.main()

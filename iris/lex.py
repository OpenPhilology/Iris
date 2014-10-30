# -*- coding: utf-8 -*-
# This module contains functions for dealing with words and dictionaries,
# such as extracting words from texts, normalizing encodings, building
# symmetric deletion dictionaries, etc.

import codecs
import algorithms as alg

def cleanlines(path, encoding=u'utf-8', normalization=u'NFD'):
    """
    Read in lines from a file and return them as a sanitized list.
    """
    with codecs.open(path, u'r', encoding=encoding) as lines:
        words = []
        for line in lines:
            words.append(alg.sanitize(line, normalization=normalization))
        return words

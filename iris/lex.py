# -*- coding: utf-8 -*-
# This module contains functions for dealing with words and dictionaries,
# such as extracting words from texts, normalizing encodings, building
# symmetric deletion dictionaries, etc.

import os
import codecs
import glob
import algorithms as alg

def cleanlines(path, encoding=u'utf-8', normalization=u'NFD'):
    """
    Read in lines from a file and return them as a sanitized list.
    Non-unique linse will be repeated.
    """
    words = []
    with codecs.open(path, u'r', encoding=encoding) as lines:
        for line in lines:
            words.append(alg.sanitize(line, normalization=normalization))
    return words

def cleanwords(path, encoding=u'utf-8', normalization=u'NFD'):
    """
    Read in every word from a files as separated by lines and spaces.
    Non-unique words will be repeated as they are read in.
    """
    words = []
    with codecs.open(path, u'r', encoding=encoding) as lines:
        for line in lines:
        	for seg in line.split(u' '):
        		clean = alg.sanitize(seg, normalization=normalization)
        		if clean != u'':
        			words.append(clean)
    return words

def cleanuniquewords(path, encoding=u'utf-8', normalization=u'NFD'):
    """
    Read in lines from a file as separated by lines and spaces,
    convert them to the specified normalization, andreturn a list
    of all unique words.
    """
    return set(cleanwords(path, encoding=encoding, normalization=normalization))


def words_from_files(dirpath, encoding=u'utf-8', normalization=u'NFD'):
    """
    Create a dictionary from a directory of text files.
	All file in the given directory will be parsed.
    """
    words = []
    for filename in filter(os.path.isfile, glob.glob(dirpath + '/*')):
        words += cleanwords(filename, encoding=encoding, normalization=normalization)
    return words


def unique_words_from_files(dirpath, encoding=u'utf-8', normalization=u'NFD'):
	"""
	Create a set of unique words from a directory of text files.
	All file in the given directory will be parsed.
	"""
	return set(words_from_files(dirpath, encoding=encoding, normalization=normalization))
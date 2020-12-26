import pytest
import os, sys; 
var = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))+'/python3'
sys.path.append(var)
from plugin import *
from base import *

def multiple_lines():
    return [
            'apple head_23 ShardIdx',
            'func t(arg *PutReply){}'
            ]
def test_createRangeOfCompressedStrings_EmptyStrip():
    new_list = CompressedString.createArrayOfCompressedStrings(multiple_lines(),[])
    assert [ a  == b.getString() for (a,b) in zip(multiple_lines(),new_list)]

@pytest.fixture
def multiple_cstrings():
    return CompressedString.createArrayOfCompressedStrings(multiple_lines(),['_'])

@pytest.fixture
def one_line_c_string():
    return CompressedString('ap___ple head_23 ShardIdx)', ['_'])


def test_createRangeOfCompressedStrings(one_line_c_string):
    string = one_line_c_string.getString()
    assert 'apple head23 ShardIdx)'.lower() == string.lower()
    

def test_findMatches(one_line_c_string):
    c_word = CompressedString('Shard',['_'])
    match = findMatches(one_line_c_string.getString(),c_word.getString())[0]
    assert one_line_c_string.getString()[match[0]] == 'S'
    assert one_line_c_string.getString()[match[1]] == 'I'
    assert match[0] == 13
    assert match[1] == 18

def test_findMatches_Empty(one_line_c_string):
    c_word = CompressedString('abs',['_'])
    matches = findMatches(one_line_c_string.getString(),c_word.getString())
    if matches:
        assert 1 == 0

def test_expandMatches(one_line_c_string):
    c_word = CompressedString('apple',['_'])
    match = findMatches(one_line_c_string.getString(),c_word.getString())[0]
    expanded_match = one_line_c_string.expandMatches([match])[0]
    assert expanded_match[0] == 0
    assert expanded_match[1] ==  8

@pytest.fixture
def textFile():
    with open('sample.py','r') as f:
        return f.readlines()

def test_translateMatches(textFile):
    line_translator = VimTranslator(0)
    c_word = CompressedString('plugin',['_'])
    array_of_c_strings = CompressedString.createArrayOfCompressedStrings(textFile,['_']) 

    list_of_highlights = []
    for rel_line,c_string in enumerate(array_of_c_strings):
        matches = findMatches(c_string.getString(),c_word.getString())
        if not matches:
            continue
        # DPrintf("c_string = {}".format(c_string.getString()))
        # DPrintf("Output = {},{}".format(matches[0].start(),matches[0].end()))
        expanded_matches = c_string.expandMatches(matches) 
        lm_pairs = line_translator.translateMatches(rel_line,expanded_matches)
        list_of_highlights.extend(lm_pairs)
        break
    assert list_of_highlights[0] == (18,(8,14))

def test_findMatches_filterNoResults(one_line_c_string):
    c_word = CompressedString('apple',['_'])
    filter = CompressedString('DD',['_'])
    matches1 = findMatches(one_line_c_string.getString(),c_word.getString())
    assert len(matches1) == 1
    matches2 = findMatches(one_line_c_string.getString(),c_word.getString(),[filter])
    assert len(matches2) == 0


def test_findMatches_filterTwoDownToOneResult(multiple_cstrings):
    c_word = CompressedString('a',['_'])
    filter = CompressedString('head')
    matches1 = findMatches(multiple_cstrings[0].getString(),c_word.getString())
    matches2 = findMatches(multiple_cstrings[1].getString(),c_word.getString())
    assert len(matches1) + len(matches2) == 4

    filter_match1 = findMatches(multiple_cstrings[0].getString(),c_word.getString(),[filter])
    filter_match2 = findMatches(multiple_cstrings[1].getString(),c_word.getString(),[filter])
    assert len(filter_match1) == 3
    assert len(filter_match2) == 0

def test_findMatches_special_characters(one_line_c_string):
    c_word = CompressedString('apple',['_'])
    filter1 = CompressedString(')')
    filter2 = CompressedString('@')
    matches1 = findMatches(one_line_c_string.getString(),c_word.getString(),[filter1])
    matches2 = findMatches(one_line_c_string.getString(),c_word.getString(),[filter2])
    assert matches2 == []
    assert len(matches1) == 1

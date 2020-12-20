import pynvim
import re

import os, sys; sys.path.append(os.path.dirname(os.path.realpath(__file__)))
from base import *
from nvim_client import *


a = 1000 # since this works, this means that a python process is spun up and waiting in the background to run these "handlers"
@pynvim.plugin
class Jumper(object):
    def __init__(self,vim):
        self.vim = vim
        DPrintf("Type of Vim: "+str(type(vim)))
        self.o_window_buffer_pair = None
        self.j_window_buffer_pair = None
        self.type = None
    @pynvim.command("OpenJumpBufferDown", nargs=0, sync=True)
    def open_jump_buffer(self):
        self.type = "Down"
        self.o_window_buffer_pair = WindowBufferPair(
                self.vim.current.window,
                self.vim.current.buffer,
                self.vim
                )
        self.vim.command("belowright split")
        self.vim.command("e JumpBuffer")
        self.vim.command("setlocal buftype=nofile")
        self.vim.command('setlocal filetype=JumpBuffer')
        self.vim.current.window.height = 1
        self.vim.command("CocDisable")
        self.j_window_buffer_pair = WindowBufferPair(
                self.vim.current.window,
                self.vim.current.buffer,
                self.vim)
        self.vim.command("startinsert")

        self.compressed_lines = None

    @pynvim.autocmd("TextChangedI", pattern='JumpBuffer', sync=True)
    def buffer_complete(self):
        # 1. get current word in JumpBuffer
        # TODO: more than just a word
        c_word, filters = extractWordAndFilters(self.vim.current.line,self.strip_set)
        if len(c_word.getString()) < 2:
            return
        # 2. get whether look up or look down -> and then create the page_content
        page_content, vim_translator = self.vim.getLineRange(self.o_window_buffer_pair,self.search_direction)
        array_of_c_strings = CompressedString.createArrayOfCompressedStrings(page_content,self.strip_set)

        self.list_of_highlights = []
        for rel_line,c_string in enumerate(array_of_c_strings):
            matches = findMatches(c_string,c_word,filters)
            if not matches:
                continue
            expanded_matches = c_string.expandMatches(matches) 
            lm_pairs = vim_translator.translateMatches(rel_line,expanded_matches)

            self.list_of_highlights.extend(lm_pairs)


        # DPrintf("list_of_highlights: {}".format(list_of_highlights))
        self.vim.addHighlights(self.list_of_highlights,self.o_window_buffer_pair,self.ns)


################ **Helpers** ##################
def extractWordAndFilters(input,strip_set):
    input = input.split(' ')

    c_word = input[0]
    c_word = CompressedString(c_word,strip_set)

    if len(input) > 1:
        c_filters = [CompressedString(x,strip_set) for x in input[1:]]
    else:
        c_filters = []

    return c_word,c_filters
def findMatches(c_string,c_word,list_of_c_filters=[]):
    """
    Note: match.end()  returns 1 over, just like C++
    """
    matches = _findCWordInCString(c_word,c_string)
    # TODO: search order changes depending on search up or search down
    for c_filter in list_of_c_filters:
        if not _findCWordInCString(c_filter,c_string):
            return []
    return matches

def _findCWordInCString(c_word,c_string):
    return [ x for x in re.finditer(c_word.getString(),c_string.getString())]

def printCurrJumpList(wb_pair,num):
    jump_list1 = wb_pair.vim.call("getjumplist",wb_pair.window)
    # win_info = wb_pair.vim.call("getwininfo",wb_pair.window)
    # DPrintf("Window Info: "+ str(win_info))
    # DPrintf("\n")
    DPrintf("JumpList" + str(num)+": "+ str(jump_list1))



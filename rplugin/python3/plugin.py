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
        c_word = self.vim.current.line
        if len(c_word) < 2:
            return
        c_word = CompressedString(c_word,self.vim.getSetOfStripCharacters())
        # 2. get whether look up or look down -> and then create the page_content
        page_content, vim_translator = self.vim.getLineRange(self.o_window_buffer_pair,self.type)
        array_of_c_strings = CompressedString.createArrayOfCompressedStrings(page_content,self.vim.getSetOfStripCharacters())

        list_of_highlights = []
        for rel_line,c_string in enumerate(array_of_c_strings):
            matches = findMatches(c_string,c_word)
            if not matches:
                continue
            expanded_matches = c_string.expandMatches(matches) 
            lm_pairs = vim_translator.translateMatches(rel_line,expanded_matches)

            list_of_highlights.extend(lm_pairs)


        self.vim.addHighlights(list_of_highlights,self.o_window_buffer_pair)
        # cursor(lnum,col)



################ **Helpers** ##################
def findMatches(c_string,c_word):
    """
    Note: match.end()  returns 1 over, just like C++
    """
    # TODO: search order changes depending on search up or search down
    return [ x for x in re.finditer(c_word.getString(),c_string.getString())]


def printCurrJumpList(wb_pair,num):
    jump_list1 = wb_pair.vim.call("getjumplist",wb_pair.window)
    # win_info = wb_pair.vim.call("getwininfo",wb_pair.window)
    # DPrintf("Window Info: "+ str(win_info))
    # DPrintf("\n")
    DPrintf("JumpList" + str(num)+": "+ str(jump_list1))



import pynvim

import os, sys; sys.path.append(os.path.dirname(os.path.realpath(__file__)))
from base import *


a = 1000 # since this works, this means that a python process is spun up and waiting in the background to run these "handlers"
@pynvim.plugin
class Jumper(object):
    def __init__(self,vim):
        # Interacting with Vim
        self.vim = vim # should only be used to setup window buffer pairs -> this way you always know which buffer you are acting on
        self.o_window_buffer = None
        self.j_window_buffer = None

        # Search Related
        self.strip_set = vim.vars.get("set_of_strip_characters",[])
        # Highlight + Selection Related
        self.highlighter = Highlighter(self.vim.request("nvim_create_namespace",""))
        # Hotkeys
        self.keymaps = {
            "<C-n>": "JumpBufferNextMatch",
            "<C-p>": "JumpBufferPrevMatch",
            "<CR>": "JumpBufferSelect",
            "<C-f>": "JumpBufferSelect",
            "<C-c>" : "JumpBufferExit"
        }

    @pynvim.command("JumpBufferOpen", nargs=0, sync=True)
    def open_jump_buffer(self):
        self.o_window_buffer = WindowBufferPair(
                self.vim.current.window,
                self.vim.current.buffer,
                self.vim
                )
        self.vim.command("belowright split")
        self.vim.command("e JumpBuffer")
        self.vim.command("setlocal buftype=nofile")
        self.vim.command('setlocal filetype=JumpBuffer')
        for k in self.keymaps:
            self.vim.command(f"inoremap <buffer> {k} <ESC>:{self.keymaps[k]}<CR>")
        self.vim.current.window.height = 1
        self.vim.command("CocDisable")
        self.j_window_buffer = WindowBufferPair(
                self.vim.current.window,
                self.vim.current.buffer,
                self.vim)
        self.vim.command("startinsert")

        # self.compressed_lines = None // maybe do optimization later

    @pynvim.autocmd("TextChangedI", pattern='JumpBuffer', sync=True)
    def buffer_complete(self):
        # 1. get current word in JumpBuffer
        # TODO: more than just a word
        c_word, filters = extractWordAndFilters(self.j_window_buffer.getCurrLine(),self.strip_set)
        if len(c_word.getString()) < 2:
            return
        # 2. get whether look up or look down -> and then create the page_content
        page_content, vim_translator = self.o_window_buffer.getLineRange()
        array_of_c_strings = CompressedString.createArrayOfCompressedStrings(page_content,self.strip_set)

        new_highlights = []
        for rel_line,c_string in enumerate(array_of_c_strings):
            matches = findMatches(c_string,c_word,filters)
            if not matches:
                continue
            expanded_matches = c_string.expandMatches(matches) 
            lm_pairs = vim_translator.translateMatches(rel_line,expanded_matches)

            new_highlights.extend(lm_pairs)
        self.highlighter.updateHighlights(new_highlights)


        self.o_window_buffer.drawHighlights(self.highlighter)
    @pynvim.command("JumpBufferNextMatch",nargs=0,sync=True)
    def next_match(self):
        # BC: No current_highlight
        # TODO: move in circular buffer?
        # 1. change highlighter struct
        # 2. redraw
        self.o_window_buffer.drawHighlights(self.highlighter)



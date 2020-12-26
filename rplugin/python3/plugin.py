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
        self.strip_set = vim.vars.get("filter_jump_strip_characters",['_'])
        # Highlight + Selection Related
        self.highlighter = None
        # Hotkeys
        self.keymaps = {}
        user_keymaps = vim.vars.get("filter_jump_keymaps",{})
        if user_keymaps is not None:
            for key,command in user_keymaps.items():
                self.keymaps[key] = command
        else:
            self.keymaps = {
                "<C-n>": "JumpBufferNextMatch",
                "<C-p>": "JumpBufferPrevMatch",
                "<CR>": "JumpBufferSelect",
                "<C-f>": "JumpBufferSelect",
                "<C-c>" : "JumpBufferExit"
            }

    @pynvim.command("FilterJumpLineForward", nargs=0, sync=True)
    def open_jump_buffer_forward(self):
        self.type = "Forward"
        self._open_jump_buffer("FilterJumpLineForward")
    @pynvim.command("FilterJumpLineBackward", nargs = 0, sync = True)
    def open_jump_buffer_backward(self):
        self.type = "Backward"
        self._open_jump_buffer("FilterJumpLineBackward")
    @pynvim.command("FilterJump", nargs=0, sync=True)
    def open_filter_jump(self):
        self.type = "Regular"
        self._open_jump_buffer("FilterJump")
    def _open_jump_buffer(self,filetype):
        self.o_window_buffer = WindowBufferPair(
                self.vim.current.window,
                self.vim.current.buffer,
                self.vim
                )
        # set here so highlighter gets reset between every jump call
        self.highlighter = Highlighter(self.vim.request("nvim_create_namespace",""))
        self.vim.command("belowright split")
        self.vim.command("e FilterJump")
        self.vim.command("setlocal buftype=nofile")
        self.vim.command("setlocal noswapfile")
        self.vim.command("setlocal nobuflisted")
        self.vim.command('setlocal filetype='+filetype)
        for key,command in self.keymaps.items():
            self.vim.command(f"inoremap <buffer> {key} <ESC>:{command}<CR>")
        self.vim.current.window.height = 1
        options = self.vim.vars.get("filter_jump_buffer_options")
        if options is not None:
            for buffer_specific_option in options:
                self.vim.command(buffer_specific_option)
        self.j_window_buffer = WindowBufferPair(
                self.vim.current.window,
                self.vim.current.buffer,
                self.vim)
        self.vim.call("deletebufline",self.j_window_buffer.buffer,1,"$")
        self.vim.command("startinsert!")

        # self.compressed_lines = None // maybe do optimization later

    @pynvim.autocmd("TextChangedI", pattern='FilterJump,FilterJumpLineForward,FilterJumpLineBackward', sync=True)
    def begin_matcher(self):
        if self.type == "Regular":
            self._doPageWideSearch()
        else:
            self._doOneLineSearch()

    def _doOneLineSearch(self):
        # 1. Get current word
        word = self.j_window_buffer.getCurrLine()
        # 2. Create the page content
        page_content, vim_translator = self.o_window_buffer.t_getLineRangeAndTranslator(self.type)
        line_content = page_content[0]

        # 3. Backend Matching
        matches = findMatches(line_content,word)
        new_highlights = vim_translator.translateMatches(0,matches)

        # 4. Highlighting
        self.highlighter.t_updateHighlighter(new_highlights,self.type)
        self.o_window_buffer.drawHighlights(self.highlighter)


    def _doPageWideSearch(self):
        # 1. Get current word in FilterJump
        c_word, filters = extractCWordAndFilters(self.j_window_buffer.getCurrLine(),self.strip_set)
        if len(c_word.getString()) < 2:
            self.o_window_buffer.clearHighlights(self.highlighter)
            return
        # 2. Create the page_content
        page_content, vim_translator = self.o_window_buffer.t_getLineRangeAndTranslator(self.type)
        array_of_c_strings = CompressedString.createArrayOfCompressedStrings(page_content,self.strip_set)

        # 3. Backend Matching
        new_highlights = []
        for rel_line,c_string in enumerate(array_of_c_strings):
            matches = findMatches(c_string.getString(),c_word.getString(),filters)
            expanded_matches = c_string.expandMatches(matches) 
            lm_pairs = vim_translator.translateMatches(rel_line,expanded_matches)

            new_highlights.extend(lm_pairs)

        # 4. Highlighting
        self.highlighter.t_updateHighlighter(new_highlights,self.type)
        self.o_window_buffer.drawHighlights(self.highlighter)

    @pynvim.command("FilterJumpNextMatch",nargs=0,sync=True)
    def next_match(self):
        # 1. change highlighter struct
        self.highlighter.incrementIndex()
        # 2. redraw
        self.o_window_buffer.drawHighlights(self.highlighter)
        self.vim.command("startinsert!")
    @pynvim.command("FilterJumpPrevMatch",nargs=0,sync=True)
    def prev_match(self):
        self.highlighter.decrementIndex()
        self.o_window_buffer.drawHighlights(self.highlighter)
        self.vim.command("startinsert!")
    @pynvim.command("FilterJumpSelect",nargs=0,sync=True)
    def select(self):
        # NOTE: below method needs to be called first to prevent vim from "scrolling" your view down + in case we call a vim command that doesn't allow you to pass in the window/buffer afterwards
        self.j_window_buffer.destroyWindowBuffer()

        self.o_window_buffer.setCursor(self.highlighter.getCurrentMatch())
        self.o_window_buffer.clearHighlights(self.highlighter)
    @pynvim.command("FilterJumpExit",nargs=0,sync=True)
    def exit(self):
        self.j_window_buffer.destroyWindowBuffer()
        self.o_window_buffer.clearHighlights(self.highlighter)
    @pynvim.command("FilterJumpVimExit",nargs=0,sync=True)
    def vim_exit(self):
        self.o_window_buffer.clearHighlights(self.highlighter)

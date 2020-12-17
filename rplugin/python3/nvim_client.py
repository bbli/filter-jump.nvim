from pynvim import api
from plugin import *

import os, sys; sys.path.append(os.path.dirname(os.path.realpath(__file__)))
from base import *
################ **Dynamically Method Adding** ##################
def getLineRange(vim,wb_pair, type):
    cursor,_ = wb_pair.getCurrCursorForced() # line number is absolute
    abs_top = None
    abs_bottom = None
    if type == "Up":
        abs_top = getLineNumberFromWindowMotion(wb_pair,"H")
        abs_bottom = cursor
    elif type == "Down":
        abs_top = cursor
        abs_bottom = getLineNumberFromWindowMotion(wb_pair,"L") # number already accounts for resize due to JumpBuffer
    else:
        DPrintf("shouldntt reach here")

    page_content = vim.call("getbufline",wb_pair.buffer,abs_top,abs_bottom)
    return page_content,AbsLineTranslator(abs_top,abs_bottom)
def getSetOfStripCharacters(vim):
    return vim.vars.get("set_of_strip_characters",[])

def addHighlights(vim,abs_expanded_lm_pairs,window_buffer_pair):
    buffer = window_buffer_pair.buffer
    new_ns = vim.request("nvim_create_namespace","")

    for (l,match_range) in abs_expanded_lm_pairs:
        vim.request("nvim_buf_add_highlight",buffer,new_ns,"SearchHighlight",l,match_range[0],match_range[1])



setattr(api.Nvim,'getLineRange',getLineRange)
setattr(api.Nvim,'getSetOfStripCharacters',getSetOfStripCharacters)
setattr(api.Nvim,'addHighlights',addHighlights)

################ **Helpers for Methods Above** ##################
def getLineNumberFromWindowMotion(wb_pair, motion):
    # check jumplist doesn't get added to
    curr_cursor = wb_pair.getCurrCursorForced()

    # switch windows and make the move
    wb_pair.vim.call("win_gotoid",wb_pair.window) # now that we are back, nothing happens
    wb_pair.vim.command("keepjumps normal! " + motion) # w/o keep jumps, JumpList will add curr location to jumplist
    new_row,_ = wb_pair.getCurrCursorForced()

    # move back
    wb_pair.vim.call("cursor",curr_cursor[0],curr_cursor[1]) # Note: does not add to jumplist
    ## testing code
    # x,y = wb_pair.getCurrCursorForced()
    # if x != curr_cursor[0] or y != curr_cursor[1]:
        # DPrintf(curr_cursor)
        # DPrintf("\n")
        # DPrintf(str(x) + ","+str(y))
        # raise AssertionError
    return new_row

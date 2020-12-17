from pynvim import api
from plugin import *

def getLineRange(vim,wb_pair, type):
    ow_cursor_x,_ = wb_pair.getCurrCursorForced() # line number is absolute
    if type == "Up":
        ow_top_line = getLineNumberFromWindowMotion(wb_pair,"H")
        page_content = vim.call("getbufline",wb_pair.buffer,ow_top_line,ow_cursor_x)
        return AbsLineTranslator(page_content,ow_top_line,ow_cursor_x)
    elif type == "Down":
        ow_bottom_line = getLineNumberFromWindowMotion(wb_pair,"L") # number already accounts for resize due to JumpBuffer
        page_content = vim.call("getbufline",wb_pair.buffer,ow_cursor_x,ow_bottom_line)
        return AbsLineTranslator(page_content,ow_cursor_x,ow_bottom_line)
    else:
        DPrintf("shouldntt reach here")

def AddHighlights(vim,abs_expanded_lm_pairs,buffer):
    new_ns = vim.request("nvim_create_namespace","")
    for (l,match_span) in abs_expanded_lm_pairs:
        vim.request("nvim_buf_add_highlight",buffer,new_ns,"SearchHighlight",l,match_span[0],match_span[1])

setattr(api.Nvim,'getLineRange',getLineRange)

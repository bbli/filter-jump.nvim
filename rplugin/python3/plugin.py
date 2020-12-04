import pynvim
import re

a = 1000 # since this works, this means that a python process is spun up and waiting in the background to run these "handlers"

log_file = open('log.txt','w')
def DPrintf(stringable):
    log_file.write(str(stringable))
    log_file.write('\n')
    log_file.flush()

class WindowBufferPair(object):
    def __init__(self,window,buffer,vim):
        self.window = window
        self.buffer = buffer

        # for calling vim
        self.vim = vim
    # TODO: invalidate cache after search finishes
    def getCurrCursorForced(self):
        return self.vim.request("nvim_win_get_cursor",self.window)

class AbsLineTranslator(object):
    def __init__(self,range,abs_top,abs_bottom):
        if len(range) != abs_bottom-abs_top+1:
            DPrintf(len(range))
            DPrintf(abs_top)
            DPrintf(abs_bottom)
            raise ArithmeticError
        self.abs_top = abs_top
        self.abs_bottom = abs_bottom
        self.range = range
    def translate(self,rel_line):
        return self.abs_top + rel_line

def createCompressedLines(range,set_of_strip_characters):
    compressed_range = []
    for string in range:
        new_string = []
        index_map = []
        for i,char in enumerate(string.lower()):
            if char not in set_of_strip_characters:
                new_string.append(char)
                index_map.append(i)
        new_string = ''.join(new_string)
        compressed_range.append(CompressedString(new_string,index_map))
    return compressed_range

class CompressedString(object):
    def __init__(self,string,index_map):
        self.string = string
        self.index_map = index_map
    def getString(self):
        return self.string
    def expand(self,match):
        return self.index_map[match.start()], self.index_map[match.end()]


@pynvim.plugin
class Jumper(object):
    def __init__(self,vim):
        self.vim = vim
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
        jw_word = self.vim.current.line
        if len(jw_word) < 2:
            return
        # 2. get whether look up or look down -> and then create the range
        # TODO: seperate line_obj and range
        line_obj = getLineRange(self.vim,self.o_window_buffer_pair,self.type)
        compressed_lines = createCompressedLines(line_obj.range,
                self.getGlobalVariable("set_of_strip_characters",[])
                )
        lm_pairs = doFilter(compressed_lines,jw_word)
        expanded_lm_pairs = [ (line,compressed_lines[line].expand(match)) for (line,match) in lm_pairs]
        abs_expanded_lm_pairs = [ (line_obj.translate(line),match_span) for (line,match_span) in expanded_lm_pairs]

        AddHighlights(self.vim,abs_expanded_lm_pairs,self.o_window_buffer_pair.buffer)
        # cursor(lnum,col)

    def getGlobalVariable(self,string_name,default):
        return self.vim.vars.get(string_name,default)


################ **Helpers** ##################
def AddHighlights(vim,abs_expanded_lm_pairs,buffer):
    new_ns = vim.request("nvim_create_namespace","")
    for (l,match_span) in abs_expanded_lm_pairs:
        vim.request("nvim_buf_add_highlight",buffer,new_ns,"SearchHighlight",l,match_span[0],match_span[1])

def doFilter(compressed_lines,word):
    list_of_matches = [] # tuples of (line_number, match_object)
    # TODO: search order changes depending on search up or search down
    for i,line in enumerate(compressed_lines):
        results = re.finditer(word,line.getString())
        for match in results:
            list_of_matches.append((i,match))
    return list_of_matches

def getLineRange(vim,wb_pair, type):
    ow_cursor_x,_ = wb_pair.getCurrCursorForced() # line number is absolute
    if type == "Up":
        ow_top_line = getLineNumberFromWindowMotion(wb_pair,"H")
        range = vim.call("getbufline",wb_pair.buffer,ow_top_line,ow_cursor_x)
        return AbsLineTranslator(range,ow_top_line,ow_cursor_x)
    elif type == "Down":
        ow_bottom_line = getLineNumberFromWindowMotion(wb_pair,"L") # number already accounts for resize due to JumpBuffer
        range = vim.call("getbufline",wb_pair.buffer,ow_cursor_x,ow_bottom_line)
        return AbsLineTranslator(range,ow_cursor_x,ow_bottom_line)
    else:
        DPrintf("shouldntt reach here")


def printCurrJumpList(wb_pair,num):
    jump_list1 = wb_pair.vim.call("getjumplist",wb_pair.window)
    # win_info = wb_pair.vim.call("getwininfo",wb_pair.window)
    # DPrintf("Window Info: "+ str(win_info))
    # DPrintf("\n")
    DPrintf("JumpList" + str(num)+": "+ str(jump_list1))


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

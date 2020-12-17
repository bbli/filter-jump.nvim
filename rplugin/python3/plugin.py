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
    def __init__(self,page_content: list,abs_top:int,abs_bottom:int):
        if len(page_content) != abs_bottom-abs_top+1:
            DPrintf(len(page_content))
            DPrintf(abs_top)
            DPrintf(abs_bottom)
            raise ArithmeticError
        self.abs_top = abs_top
        self.abs_bottom = abs_bottom
        self.page_content = page_content
    def translate(self,rel_line):
        return self.abs_top + rel_line
    def translateMatches(self,rel_line,list_of_ranges):
        return [(self.translate(rel_line),range) for range in list_of_ranges]


class CompressedString(object):
    def __init__(self,string,index_map):
        self.string = string
        self.index_map = index_map
    def getString(self):
        return self.string
    def expand(self,start,end):
        return self.index_map[start], self.index_map[end]
    def expandMatches(self,matches):
        return [self.expand(match.start(),match.end()) for match in matches]
    @classmethod
    def createArrayOfCompressedStrings(cls,page_content,set_of_strip_characters):
        self.getGlobalVariable("set_of_strip_characters",[])
        compressed_range = []
        for string in page_content:
            new_string = []
            index_map = []
            for i,char in enumerate(string.lower()):
                if char not in set_of_strip_characters:
                    new_string.append(char)
                    index_map.append(i)
            new_string = ''.join(new_string)
            compressed_range.append(CompressedString(new_string,index_map))
        return compressed_range


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
        jw_word = self.vim.current.line
        if len(jw_word) < 2:
            return
        # 2. get whether look up or look down -> and then create the page_content
        # TODO: seperate line_obj and page_content
        page_content, line_translator = self.vim.getLineRange(self.o_window_buffer_pair,self.type)
        array_of_c_strings = CompressedString.createArrayOfCompressedStrings(page_content)

        list_of_highlights = []
        for rel_line,c_string in enumerate(array_of_c_strings):
            matches = findMatches(c_string,jw_word)
            # Q: make both of these methods?
            expanded_matches = c_string.expandMatches(matches) 
            lm_pairs = line_translator.translateMatches(rel_line,expanded_matches)

            list_of_highlights.extend(lm_pairs)


        self.vim.AddHighlights(list_of_highlights,self.o_window_buffer_pair)
        # cursor(lnum,col)

    def getGlobalVariable(self,string_name,default):
        return self.vim.vars.get(string_name,default)


################ **Helpers** ##################

def findMatches(compressed_lines,word):
    list_of_matches = [] # tuples of (line_number, match_object)
    # TODO: search order changes depending on search up or search down
    for i,line in enumerate(compressed_lines):
        results = re.finditer(word,line.getString())
        for match in results:
            list_of_matches.append((i,match))
    return list_of_matches



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

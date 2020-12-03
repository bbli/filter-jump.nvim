import pynvim
import re

a = 1000 # since this works, this means that a python process is spun up and waiting in the background to run these "handlers"

log_file = open('log.txt','w')
def DPrintf(stringable):
    log_file.write(str(stringable))
    log_file.write('\n')
    log_file.flush()
    

# @pynvim.plugin
# class Limit(object):
    # def __init__(self, vim):
        # self.vim = vim
        # self.calls = 0

    # @pynvim.command('Cmd2', range='', nargs='*', sync=True)
    # def command_handler(self, args, range):
        # self._increment_calls()
        # self.vim.current.line = (
            # 'Command: Called %d times, args: %s, range: %s' % (self.calls,
                                                               # args,
                                                               # range))

    # @pynvim.autocmd('BufEnter', pattern='*.txo', eval='expand("<afile>")',
                    # sync=True)
    # def autocmd_handler(self, filename):
        # self._increment_calls()
        # DPrintf(dir(self.vim.buffers))
        # DPrintf("HII")
        # self.vim.current.line = (
                # 'Autocmd: Called %s times, file: %s var: %s' % (self.calls, filename,a))

    # @pynvim.function('Func')
    # def function_handler(self, args):
        # self._increment_calls()
        # self.vim.current.line = (
            # 'Function: Called %d times, args: %s' % (self.calls, args))

    # def _increment_calls(self):
        # # if self.calls == 5:
            # # raise Exception('Too many calls!')
        # self.calls += 1

class WindowBufferPair(object):
    def __init__(self,window,buffer,vim):
        self.window = window
        self.buffer = buffer

        # for calling vim
        self.vim = vim
    # TODO: invalidate cache after search finishes
    def getCurrCursorForced(self):
        return self.vim.request("nvim_win_get_cursor",self.window)

class LineTranslator(object):
    def __init__(self,range,abs_top,abs_bottom):
        if len(range) != abs_top-abs_bottom+1:
            raise ArithmeticError
        self.abs_top = abs_top
        self.abs_bottom = abs_bottom
        self.range = range

@pynvim.plugin
class Jumper(object):
    def __init__(self,vim):
        self.vim = vim
        self.o_window_buffer_pair = None
        self.j_window_buffer_pair = None
        self.type = None
    @pynvim.command("OpenJumpBufferUp", nargs=0, sync=True)
    def open_jump_buffer(self):
        self.type = "Up"
        self.o_window_buffer_pair = WindowBufferPair(
                self.vim.current.window,
                self.vim.current.buffer,
                self.vim
                )
        self.vim.command("split")
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

    @pynvim.autocmd("TextChangedI", pattern='JumpBuffer', sync=True)
    def buffer_complete(self):
        # 1. get current word in JumpBuffer
        jw_word = self.vim.current.line
        if len(jw_word) < 2:
            return
        # 2. get whether look up or look down -> and then create the range
        line_obj = self._getLineRange(self.o_window_buffer_pair,self.type)
        # DPrintf(lines)
        
        # matches = do_filter(line_obj.range,jw_word)

        # self.vim.request("nvim_buf_add_highlight",buffer,ns,hl_group,line,col_start,col_end)
        # cursor(lnum,col)


    def _getLineRange(self,wb_pair, type):
        ow_cursor_x,_ = wb_pair.getCurrCursorForced() # line number is absolute
        if type == "Up":
            ow_top_line = getLineNumberFromWindowMotion(wb_pair,"H")
            range = self.vim.call("getbufline",wb_pair.buffer,ow_top_line,ow_cursor_x)
            return LineTranslator(range,ow_top_line,ow_cursor_x)
        elif type == "Down":
            ow_bottom_line = getLineNumberFromWindowMotion(wb_pair,"L") # number already accounts for resize due to JumpBuffer
            range = self.vim.call("getbufline",wb_pair.buffer,ow_cursor_x,ow_bottom_line)
            return LineTranslator(range,ow_cursor_x,ow_bottom_line)
        else:
            DPrintf("shouldntt reach here")


################ **Helpers** ##################
def do_filter(lines,word):
    list_of_matches = []
    # TODO: search order changes depending on search up or search down
    for i,line in enumerate(lines):
        results = re.finditer(word,transform(line))
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
    wb_pair.vim.command("keepjumps normal! " + motion) # w/o keep jumps, JumpList will add curr location to jumplist -> But doesn't matter since we are going to come back anyways?
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

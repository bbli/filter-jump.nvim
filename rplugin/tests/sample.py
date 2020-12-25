import pynvim

a = 1000 # since this works, this means that a python process is spun up and waiting in the background to run these "handlers"

log_file = open('log.txt','w')
def DPrintf(stringable):
    log_file.write(str(stringable))
    log_file.write('\n')
    log_file.flush()
    


class WindowBufferPair(object):
    def __init__(self,window,buffer):
        self.window = window
        self.buffer = buffer


@pynvim.plugin
class Jumper(object):
    def __init__(self,vim):
        self.vim = vim
        self.o_window_buffer_pair = None
        self.j_window_buffer_pair = None
        self.type = None
    @pynvim.command("OpenFilterJumpUp", nargs=0, sync=True)
    def open_jump_buffer(self):
        self.type = "Up"
        self.o_window_buffer_pair = WindowBufferPair(self.vim.current.window,self.vim.current.buffer)
        self.vim.command("split")
        self.vim.command("e FilterJump")
        self.vim.command("setlocal buftype=nofile")
        self.vim.command('setlocal filetype=FilterJump')
        self.vim.current.window.height = 1
        self.vim.command("CocDisable")
        self.j_window_buffer_pair = WindowBufferPair(self.vim.current.window,self.vim.current.buffer)
        self.vim.command("startinsert")

    @pynvim.autocmd("TextChangedI", pattern='JumpBuffer', sync=True)
    def buffer_complete(self):
        # 1. get current word in JumpBuffer
        jw_word = self.vim.current.line
        # 2. get whether look up or look down -> and then create the range
        lines = self._getLineRange(self.o_window_buffer_pair,self.type)

        # self.vim.request("nvim_buf_add_highlight",buffer,ns,hl_group,line,col_start,col_end)
        # cursor(lnum,col)


    def _getLineRange(self,wb_pair, type):
            # cursor = vim.call("line",".")
            ow_cursor_x, _ = self.vim.request("nvim_win_get_cursor",wb_pair.window)
            # DPrintf("cursor's line number: "+str(ow_cursor_x))
            if type == "Up":
                return self.vim.call("getbufline",wb_pair.buffer,1,ow_cursor_x)
            elif type == "Down":
                return self.vim.call("getbufline",wb_pair.buffer,ow_cursor_x,"$")
            else:
                DPrintf("shouldntt reach here")

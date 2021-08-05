import pynvim
import re

def DPrintf(stringable):
    if 'log_file' not in globals():
        global log_file
        log_file = open('log.txt','w')

    log_file.write(str(stringable))
    log_file.write('\n')
    log_file.flush()

def debug(f):
    def wrapper(*args):
        result = f(*args)
        DPrintf("Function Name = {} Output = {}".format(f.__name__,result))
        return result
    return wrapper
################ **** ##################
# TODO: all vim interactions should be done via this object
class WindowBufferPair(object):
    def __init__(self,window,buffer,vim):
        self.window = window
        self.buffer = buffer

        # for calling vim
        self.vim = vim
    def _getCurrCursorForced(self):
        """
        Note: This will be 1 indexed in x and 0 indexed in y
        """
        return self.vim.request("nvim_win_get_cursor",self.window)
    def setCursor(self,l_match):
        """
        Note: Row + Column is now 1 indexed b/c we changed to executing a direct vim command
        """
        #EC: we pressed enter when there was no match. In which case, just go back w/o moving the cursor
        if not l_match:
            return
        r = l_match[0]+1
        c = l_match[1][0]+1
        self.vim.request("nvim_exec","normal{}G{}| ".format(r,c),False)
    def getCurrLine(self):
        line_num,_ = self._getCurrCursorForced()
        result = self.vim.request("nvim_buf_get_lines",self.buffer,line_num-1,line_num,True)
        # DPrintf("Result: {}".format(result))
        # DPrintf("Vim Current Line: {}".format(self.vim.current.line))
        # assert result[0] == self.vim.current.line
        return result[0]
    def t_getLineRangeAndTranslator(self,type):
        if type == "Regular":
            abs_top = self._getLineFromWindowMotion("H")
            abs_bottom = self._getLineFromWindowMotion("L") # number already accounts for resize due to FilterJump
            page_content = self.vim.call("getbufline",self.buffer,abs_top,abs_bottom)
            return page_content,VimTranslator(abs_top-1)#Since vim calls are 1 indexed
        elif type == "Forward":
            page_content = self.getCurrLine()
            row, col = self._getCurrCursorForced()

            page_content = _onlyKeepCharactersInFront(page_content, col+1)
            return page_content,VimTranslator(row-1,col+1)
        else:
            if type != "Backward":
                raise Exception

            page_content = self.getCurrLine()
            row, col = self._getCurrCursorForced()

            page_content = _onlyKeepCharactersInBack(page_content,col)
            return page_content,VimTranslator(row-1,0) # col doesn't need to be offset here

    # @debug
    def _getLineFromWindowMotion(self, motion):
        curr_cursor = self._getCurrCursorForced()

        # 1.switch windows and make the move
        self.vim.call("win_gotoid",self.window) # now that we are back, nothing happens
        self.vim.command("keepjumps normal! " + motion) # w/o keep jumps, JumpList will add curr location to jumplist
        new_row,_ = self._getCurrCursorForced()

        # 2.move back
        self.vim.call("cursor",curr_cursor[0],curr_cursor[1]) # Note: does not add to jumplist
        ## testing code
        # x,y = wb_pair._getCurrCursorForced()
        # if x != curr_cursor[0] or y != curr_cursor[1]:
            # DPrintf(curr_cursor)
            # DPrintf("\n")
            # DPrintf(str(x) + ","+str(y))
            # raise AssertionError
        return new_row
    def drawHighlights(self,highlighter):
        """
        Note: match_range should be exclusive at end
        Note: 0 indexed horizontally and vertically, despite vim frontend being otherwise
        """
        self.clearHighlights(highlighter)
        # EC: highlights + match are None
        if not highlighter.getCurrentMatch():
            return

        # 1. Highlight current selection
        first_line,first_match = highlighter.getCurrentMatch()
        self.vim.request("nvim_buf_add_highlight",self.buffer,highlighter.ns,"SearchCurrent",first_line,first_match[0],first_match[1])
        # 2. Highlight rest
        for (l,match) in highlighter.list_of_highlights:
            if l != first_line or match !=first_match:
                self.vim.request("nvim_buf_add_highlight",self.buffer,highlighter.ns,"SearchHighlights",l,match[0],match[1])
    def clearHighlights(self,highlighter):
        self.vim.request("nvim_buf_clear_namespace",self.buffer,highlighter.ns,0,-1)
    def destroyWindowBuffer(self):
        self.vim.request("nvim_buf_delete",self.buffer,{})

################ **** ##################
class VimTranslator(object):
    def __init__(self,abs_top,x_offset = 0):
        """
        Note: This object assumes 0 indexed positions
        """
        self.abs_top = abs_top
        self.x_offset = x_offset
    def _translate_y(self,rel_line):
        return self.abs_top + rel_line
    def _translate_x(self,range):
        return (range[0]+self.x_offset,range[1]+self.x_offset)
    # @debug
    def translateMatches(self,rel_line,list_of_ranges):
        return [(self._translate_y(rel_line),self._translate_x(range)) for range in list_of_ranges]

################ **** ##################
class CompressedString(object):
    def __init__(self,string,set_of_strip_characters=['_']):
        new_string = []
        index_map = []
        # My personal preference is to ignore capital letters when making big jumps but keep it for the one line cases below
        for i,char in enumerate(string.lower()):
            if char not in set_of_strip_characters:
                new_string.append(char)
                index_map.append(i)
        new_string = ''.join(new_string)
        self.c_string = new_string
        self.index_map = index_map
        self.length = len(new_string)
    def getString(self):
        return self.c_string
    def _expand(self,start,end):
        if end == self.length:
            return self.index_map[start],self.index_map[self.length-1] +1
        else:
            return self.index_map[start], self.index_map[end]
    # @debug
    def expandMatches(self,matches):
        return [self._expand(match[0],match[1]) for match in matches]
    @staticmethod
    def createArrayOfCompressedStrings(page_content,set_of_strip_characters):
        compressed_range = []
        for string in page_content:
            compressed_range.append(CompressedString(string,set_of_strip_characters))
        return compressed_range

################ **** ##################
class Highlighter(object):
    def __init__(self,ns):
        self.ns = ns

        self.list_of_highlights = []
        # TODO: combine current_match + idx into just an iterator/refactor incrementIndex
        self.current_l_match = None
        self.idx = 0
        self.variable_to_print = None
    def t_updateHighlighter(self,list_of_highlights,type,curr_pos):
        DPrintf("curr pos passed to updateHighlighter: {}".format(curr_pos))
        # EC: no highlight matches
        if not list_of_highlights:
            self.variable_to_print = None
            self.list_of_highlights = []
            return

        # Case 1: No Previous Matches: Just make first selection current
        if type == "Forward":
            self.update_highlighter_forward(list_of_highlights)
        elif type == "Backward":
            self.update_highlighter_backward(list_of_highlights)
        else:
            self.update_highlighter_regular(list_of_highlights,curr_pos)

        self.variable_to_print = self.current_l_match
        self.list_of_highlights = list_of_highlights
    def update_highlighter_forward(self,list_of_highlights):
        if not self.current_l_match:
            self.current_l_match = list_of_highlights[0]
            self.idx = 0
        else:
            idx, new_current_l_match = _findFirstGreaterThanOrEqualToMatch(list_of_highlights,self.current_l_match)
            self.current_l_match = new_current_l_match
            self.idx = idx
    def update_highlighter_backward(self,list_of_highlights):
        if not self.current_l_match:
            self.idx = len(list_of_highlights) -1
            self.current_l_match = list_of_highlights[self.idx]
        else:
            idx, new_current_l_match = _findFirstLessThanOrEqualToMatch(list_of_highlights,self.current_l_match)
            self.idx = idx
            self.current_l_match = new_current_l_match

    def update_highlighter_regular(self,list_of_highlights,curr_pos):
        DPrintf("one entry in list_of_highlights data structure: {}".format(list_of_highlights[0]))
        if not self.current_l_match:
            # 1. Creates current selection
            # D: is curr_pos +/- 1 from self.current_l_match? Nah, should be fine
            # HACK: making up a match structure for the sake of reusing _findClosestInterval code.
            # NOTE: -1 is b/c highlights goes by 0 indexing
            idx, new_current_l_match = _findClosestInterval(list_of_highlights,
                                                        (curr_pos[0]+1,(curr_pos[1],curr_pos[1])))
            self.current_l_match = new_current_l_match
            self.idx = idx
        else:
        # Case 2: Need to track current selection vs updated matches
            idx, new_current_l_match = _findClosestInterval(list_of_highlights,self.current_l_match)
            self.current_l_match = new_current_l_match
            self.idx = idx

    def getCurrentMatch(self):
        return self.variable_to_print
    def incrementIndex(self):
        # EC: no highlights to increment from
        if self.variable_to_print == None:
            return

        # TODO: move in circular buffer?
        self.idx += 1
        if self.idx == len(self.list_of_highlights):
            self.idx = 0
        
        self.current_l_match = self.list_of_highlights[self.idx]
        self.variable_to_print = self.current_l_match
    def decrementIndex(self):
        # EC: no highlights to increment from
        if self.variable_to_print == None:
            return

        # TODO: move in circular buffer?
        self.idx -= 1
        if self.idx < 0:
            self.idx = len(self.list_of_highlights) - 1
        
        self.current_l_match = self.list_of_highlights[self.idx]
        self.variable_to_print = self.current_l_match

################ **Helpers** ##################
# @debug
def _findClosestInterval(list_of_highlights,current_l_match):
    min_dis = _calcManDistance(list_of_highlights[0],current_l_match)
    min_l_match = list_of_highlights[0]
    min_idx = 0
    for idx, l_match in enumerate(list_of_highlights[1:]):
        #TODO: early exit if distances start to increase
        DPrintf("current_l_match: {}".format(current_l_match))
        dis = _calcManDistance(l_match,current_l_match)
        if dis < min_dis:
            min_dis = dis
            min_l_match = l_match
            min_idx = idx+1
    return min_idx,min_l_match

def _calcManDistance(l_match1,l_match2):
    delta_x = l_match1[0] - l_match2[0]
    delra_y = l_match1[1][0] - l_match2[1][0]
    return abs(delta_x+delra_y)
################ **** ##################
def _findFirstGreaterThanOrEqualToMatch(list_of_highlights,current_l_match):
    current_match = current_l_match[1]
    for idx,l_match in enumerate(list_of_highlights):
        match = l_match[1]
        if match[0] >= current_match[0]:
            return idx, l_match
    return 0,list_of_highlights[0]

def _findFirstLessThanOrEqualToMatch(list_of_highlights,current_l_match):
    end = len(list_of_highlights) -1
    current_match = current_l_match[1]
    idx_so_far = end
    l_match_so_far = list_of_highlights[end]
    for idx,l_match in enumerate(list_of_highlights):
        match = l_match[1]
        if match[0] <= current_match[0]:
            idx_so_far = idx
            l_match_so_far = l_match
    return idx_so_far,l_match_so_far
    
################ **** ##################
def _findNewContainedInterval(list_of_highlights,current_l_match):
    for idx,l_match in enumerate(list_of_highlights):
        # TODO: make this a method/custom data type so usage is clearer
        if _isContainedIn(current_l_match,l_match):
            return idx,l_match
    return 0,None

def _isContainedIn(current_l_match,bigger_l_match):
    if current_l_match[0] != bigger_l_match[0]:
        return False

    smaller_range = current_l_match[1]
    bigger_range = bigger_l_match[1]
    if bigger_range[0] <= smaller_range[0] and smaller_range[1] <= bigger_range[1]:
        return True
    else:
        return False
################ **** ##################
def extractCWordAndFilters(input,strip_set):
    input = input.split(' ')

    c_word = input[0]
    c_word = CompressedString(c_word,strip_set)

    if len(input) > 1:
        c_filters = [CompressedString(x,strip_set) for x in input[1:]]
    else:
        c_filters = []

    return c_word,c_filters
################ **** ##################
# @debug
def findMatches(string,word,list_of_c_filters=[]):
    """
    Note: match.end()  returns 1 over, just like C++
    """
    matches = _findWordInString(word,string)
    # TODO: search order changes depending on search up or search down
    for c_filter in list_of_c_filters:
        if not _findWordInString(c_filter.getString(),string):
            return []
    return [(match.start(),match.end()) for match in matches]

# @debug
# def escape(word):
    # return re.escape(word)

def _findWordInString(word,string):
    word = re.escape(word)
    return [ x for x in re.finditer(word,string)]
################ **** ##################
# @debug
def _onlyKeepCharactersInFront(curr_line,curr_col):
    # EC
    if len(curr_line) < 1:
        return [curr_line]

    return [curr_line[curr_col:]]

# @debug
def _onlyKeepCharactersInBack(curr_line,curr_col):
    # EC
    if len(curr_line) < 1:
        return [curr_line]

    return [curr_line[:curr_col]]

log_file = open('log.txt','w')
def DPrintf(stringable):
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
class WindowBufferPair(object):
    def __init__(self,window,buffer,vim):
        self.window = window
        self.buffer = buffer

        # for calling vim
        self.vim = vim
    # TODO: invalidate cache after search finishes
    def getCurrCursorForced(self):
        return self.vim.request("nvim_win_get_cursor",self.window)

################ **** ##################
class VimTranslator(object):
    def __init__(self,abs_top):
        """
        Adjusting for frontend being 1 indexed while add_highlight being 0 indexed
        """
        self.abs_top = abs_top - 1
        self.x_offset = 0
    def _translate_y(self,rel_line):
        return self.abs_top + rel_line
    def _translate_x(self,range):
        return (range[0]+self.x_offset,range[1]+self.x_offset)
    # @debug
    def translateMatches(self,rel_line,list_of_ranges):
        return [(self._translate_y(rel_line),self._translate_x(range)) for range in list_of_ranges]


################ **** ##################
class CompressedString(object):
    def __init__(self,string,set_of_strip_characters):
        new_string = []
        index_map = []
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
    def inclusive_expand(self,start,end):
        if end == self.length:
            return self.index_map[start],self.index_map[self.length-1] +1
        else:
            return self.index_map[start], self.index_map[end]
    # @debug
    def expandMatches(self,matches):
        return [self.inclusive_expand(match.start(),match.end()) for match in matches]
    @classmethod
    def createArrayOfCompressedStrings(cls,page_content,set_of_strip_characters):
        """
        Note: compressed strings will also be lowercased
        """
        compressed_range = []
        for string in page_content:
            compressed_range.append(CompressedString(string,set_of_strip_characters))
        return compressed_range

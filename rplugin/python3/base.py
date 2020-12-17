log_file = open('log.txt','w')
def DPrintf(stringable):
    log_file.write(str(stringable))
    log_file.write('\n')
    log_file.flush()

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
class AbsLineTranslator(object):
    def __init__(self,abs_top,abs_bottom):
        self.abs_top = abs_top
        self.abs_bottom = abs_bottom
    def translate(self,rel_line):
        return self.abs_top + rel_line
    def translateMatches(self,rel_line,list_of_ranges):
        return [(self.translate(rel_line),range) for range in list_of_ranges]


################ **** ##################
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

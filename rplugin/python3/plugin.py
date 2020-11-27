import re
import pynvim

@pynvim.plugin
class Translator(object):
    def __init__(self, vim):
        self.vim = vim
        self.data_base = None
        self.reverse_data_base = None
        self.reTextId = re.compile('"(?P<textid>(?P<category>\d+)-(?P<number>\d+))"')
        self.reTranslated = re.compile('"--(?P<translation>[ a-zA-Z0-9.,;:!?-]*)--"')
        self.update_db()

    @pynvim.command('UpdateTextDb', sync=True)
    def update_db(self):
        self.data_base = {}
        self.reverse_data_base = {}
        db_file = self.vim.vars.get('textid_db_file')
        if db_file:
            with open(db_file, "r") as db:
                for line in db.readlines():
                    tid, text = line.strip().split('|')
                    self.data_base[tid] = text
                    self.reverse_data_base[text] = tid

    def lookup_text_id_by_match(self, matchObject):
        tid = matchObject.group("textid")
        if tid in self.data_base:
            return '"--' + self.data_base[tid] + '--"'
        else:
            self.vim.out_write(f"Unknown text ID: {tid}")
            return f'"{tid}"'

    def lookup_translated_by_match(self, matchObject):
        text = matchObject.group("translation")
        if text in self.reverse_data_base:
            return '"' + self.reverse_data_base[text] + '"'
        else:
            self.vim.out_write(f"Unknown text")
            return f'"--{text}--"'

    def toggle_line(self, line):
        if self.reTextId.search(line):
            return self.reTextId.sub(self.lookup_text_id_by_match, line)
        else:
            return self.reTranslated.sub(self.lookup_translated_by_match, line)

    @pynvim.command('ToggleTextId', range=True, nargs='*', sync=True)
    def command_handler(self, args, range):
        start, end = range
        # Range is given 1-based, but we need 0-based indexing
        lines = self.vim.current.buffer[start-1:end]
        toggled_lines = list(map(self.toggle_line, lines))
        self.vim.current.buffer[start-1:end] = toggled_lines

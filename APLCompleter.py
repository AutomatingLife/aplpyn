from apl_completions import apl_completions
from apl_descriptions import apl_descriptions
from prompt_toolkit.completion import Completer, Completion
class APLCompleter(Completer):
    def __init__(self, user_defs):
        self.user_defs = user_defs

    def get_completions(self, document, complete_event):
        last_two_chars = document.text_before_cursor[-2:].strip()
        if len(last_two_chars) != 2:
            return
        if last_two_chars in apl_completions:
            description = apl_descriptions[str(last_two_chars)]
            yield Completion(apl_completions[str(last_two_chars)], start_position=-2,
                             display_meta=description, style='bg:lightblue')

        elif any(k.startswith(document.text_before_cursor[-1:]) for k in apl_completions):
            for seq, symbol in apl_completions.items():
                if seq.startswith(document.text_before_cursor[-1:]):
                    description = apl_descriptions[seq]
                    yield Completion(symbol, start_position=-1,
                                     display_meta=description, style='bg:lightblue')
        # Check for user-defined functions and variables
        text = document.text_before_cursor.strip()
        alnumchain = list(map(str.isalnum, reversed(text)))
        alnumtext = text[-len(alnumchain):]
        if len(alnumtext) >= 3:
            for name, info in self.user_defs['functions'].items():
                if name.startswith(alnumtext):
                    yield Completion(name, start_position=-len(alnumtext), display_meta=info['comment'],
                                     style='bg:ansibrightyellow')
            for name, info in self.user_defs['variables'].items():
                if name.startswith(alnumtext):
                    yield Completion(name, start_position=-len(alnumtext), display_meta=info['comment'],
                                     style='bg:ansibrightmagenta')
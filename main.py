import json
import requests
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion

apl_completions = {
    "<-": "←",
    "xx": "×",
    ":-": "÷",
    "*O": "⍟",
    "OO": "○",
    "|_": "⊥",
    "TT": "⊤",
    "-|": "⊣",
    "|-": "⊢",
    "=/": "≠",
    "<_": "≤",
    ">_": "≥",
    "==": "≡",
    "_=": "≡",
    "vv": "∨",
    "^^": "∧",
    "^~": "⍲",
    "v~": "⍱",
    "^|": "↑",
    "v|": "↓",
    "cc": "⊂",
    "))": "⊃",
    "c_": "⊆",
    "A|": "⍋",
    "V|": "⍒",
    "ii": "⍳",
    "i_": "⍸",
    "ee": "∊",
    "e_": "⍷",
    "uu": "∪",
    "nn": "∩",
    "/-": "⌿",
    "\\-": "⍀",
    ",-": "⍪",
    "O-": "⊖",
    "O\\": "⍉",
    "~:": "⍨",
    "*:": "⍣",
    "oo": "∘",
    "o:": "⍤",
    "O:": "⍥",
    "[]": "⎕",
    "o_": "⍎",
    "o-": "⍕",
    "To": "⍕",
    "<>": "⋄",
    "on": "⍝",
    "ww": "⍵",
    "aa": "⍺",
    "VV": "∇",
    "--": "¯",
    "0~": "⍬",
    "[-": "⌹",
    "-": "⌹",
    "[|": "⌷",
    "|]": "⌷",
    "7=": "≢",
    "Z-": "≢",
    "77": "⌈",
    "FF": "⌈",
    "ll": "⌊",
    "LL": "⌊",
    "::": "¨",
    "\"\"": "¨",
    "rr": "⍴",
    "pp": "⍴",
    "[:": "⍠",
    ":]": "⍠",
    "[=": "⌸",
    "=]": "⌸",
    "[<": "⌺",
    ">]": "⌺",
    "T_": "⌶",
    "II": "⌶",
}
apl_descriptions = {
    "<-": "Assignment",
    "xx": "Direction | Times",
    ":-": "Reciprocal | Divide",
    "*O": "Natural logarithm | Logarithm",
    "OO": "Pi Times | Circular",
    "|_": "Decode (Dyadic)",
    "TT": "Encode (Dyadic)",
    "-|": "Same | Left",
    "|-": "Same | Right",
    "=/": "Unique Mask | Not equal",
    "<_": "Less than or equal to (Dyadic)",
    ">_": "Greater than or equal to (Dyadic)",
    "==": "Depth | Match",
    "_=": "Depth | Match",
    "vv": "Or (Dyadic)",
    "^^": "And (Dyadic)",
    "^~": "Nan (Dyadic)",
    "v~": "Nor (Dyadic)",
    "^|": "Mix | Take",
    "v|": "Split | Drop",
    "cc": "Enclose | Partitioned enclose",
    "))": "First | Pick",
    "c_": "Nest | Partition",
    "A|": "Grade up | Grade up",
    "V|": "Grade down | Grade down",
    "ii": "Indices | Indices of",
    "i_": "Where | Interval index",
    "ee": "Enlist | Member of",
    "e_": "Find (Dyadic)",
    "uu": "Unique | Union",
    "nn": "Intersection (Dyadic)",
    "/-": "Replicate First | Reduce First",
    "\\-": "Expand First | Scan First",
    ",-": "Table | Catenate First",
    "O-": "Reverse First | Rotate First",
    "O\\": "Transpose | Reorder Axes",
    "~:": "Constant/Commute | Self/Swap",
    "*:": "Repeat (Dyadic)",
    "oo": "Curry/Compose | Beside/Bind",
    "o:": "Rank/Atop (Dyadic)",
    "O:": "Over (Dyadic)",
    "[]": "SYSTEM",
    "o_": "Execute",
    "o-": "Format",
    "To": "Format",
    "<>": "Statement separator",
    "on": "Comment",
    "ww": "Right argument | Right operand",
    "aa": "Left argument | Left operand",
    "VV": "Recursion | Recursion",
    "--": "Negative",
    "0~": "Empty numeric vector",
    "[-": "Matrix inverse | Matrix divide",
    "-]": "Matrix inverse | Matrix divide",
    "[|": "Index",
    "|]": "Index",
    "7=": "Tally | Not match",
    "Z-": "Tally | Not match",
    "77": "Ceiling | Maximum",
    "FF": "Ceiling | Maximum",
    "ll": "Floor | Minimum",
    "LL": "Floor | Minimum",
    "::": "Each",
    "\"\"": "Each",
    "rr": "Shape | Reshape",
    "pp": "Shape | Reshape",
    "[:": "Variant",
    ":]": "Variant",
    "[=": "Index key | Key",
    "=]": "Index key | Key",
    "[<": "Stencil",
    ">]": "Stencil",
    "T_": "I-beam",
    "II": "I-beam",
}


class APLCompleter(Completer):
    def get_completions(self, document, complete_event):
        last_two_chars = document.text_before_cursor[-2:]
        if last_two_chars == '':
            return
        if last_two_chars in apl_completions:
            description = apl_descriptions[last_two_chars]
            yield Completion(apl_completions[last_two_chars], start_position=-2,
                             display_meta=description, style='bg:ansiblue')

        elif any(k.startswith(document.text_before_cursor[-1:]) for k in apl_completions):
            for seq, symbol in apl_completions.items():
                if seq.startswith(document.text_before_cursor[-1:]):
                    description = apl_descriptions[seq]
                    yield Completion(symbol, start_position=-1,
                                     display_meta=description, style='bg:ansiblue')


class APLExecutor:
    def __init__(self):
        self.url = "https://tryapl.org/Exec"
        self.headers = {'Content-Type': 'application/json; charset=utf-8'}
        self.state = ''
        self.size = 0
        self.hash = ''

    def exec(self, code):
        data = ['', 0, '', code]
        response = requests.post(self.url, headers=self.headers, data=json.dumps(data))
        data = response.json()
        return data

    def _exec_stateful(self, code):
        data = [self.state, self.size, self.hash, code]
        response = requests.post(self.url, headers=self.headers, data=json.dumps(data))
        data = response.json()
        self.state, self.size, self.hash = data[:3]
        return data

    def fn(self, code):
        def wrapped_function(*args):
            apl_code = code + ' ' + ' '.join(map(str, args))
            response = self._exec_stateful(apl_code)
            result = response[3][0] if response[3] else None
            return result

        return wrapped_function

    def clear(self):
        self.state = ''
        self.size = 0
        self.hash = ''

    def cli(self):
        session = PromptSession(completer=APLCompleter())
        print("APL CLI - type 'exit' to quit")
        while True:
            try:
                text = session.prompt('APL> ')
                if text.strip() == '⎕EXIT':
                    break
                if text.strip() == '⎕CLEAR':
                    self.clear()
                    continue
                # If the text uses ⎕NGET'filepath', replace it with the actual file contents. The contents should be an escaped string.
                if '⎕NGET' in text:
                    start = text.find('⎕NGET') + 6
                    end = text.find("'", start)
                    filepath = text[start:end]
                    with open(filepath, 'r') as f:
                        contents = f.read()
                        # Turn the string into unicode code points, separated by spaces
                        contents = ' '.join(map(str, map(ord, contents)))
                    text = f"{text[:(start-6)]}⎕UCS {contents}{text[(end+1):]}"
                # Automatically replace ASCII sequences with corresponding APL symbols
                for i in range(len(text) - 1):
                    ascii_seq = text[i:i + 2]
                    if ascii_seq in apl_completions:
                        text = text[:i] + apl_completions[ascii_seq] + text[i + 2:]
                response = self._exec_stateful(text)
                if response[3]:
                    if len(response[3]) > 1:
                        for element in response[3]:
                            print(element)
                    else:
                        print(response[3][0])
                else:
                    print('No result')
            except Exception as e:
                print(f"An error occurred: {e}")


apl = APLExecutor()

apl.cli()

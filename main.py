import json
import requests
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion
from apl_completions import apl_completions
from apl_descriptions import apl_descriptions


class APLCompleter(Completer):
    def get_completions(self, document, complete_event):
        last_two_chars = document.text_before_cursor[-2:].strip(' ')
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
                if '⎕NREAD' in text:
                    start = text.find('⎕NREAD') + 7
                    end = text.find("'", start)
                    filepath = text[start:end]
                    with open(filepath, 'r') as f:
                        contents = f.read()
                        # Turn the string into unicode code points, separated by spaces
                        contents = ' '.join(map(str, map(ord, contents)))
                    text = f"{text[:(start - 7)]}⎕UCS {contents}{text[(end + 1):]}"
                if '⎕NPUT' in text:
                    start = text.find('⎕NPUT') + 6
                    contents = text[:(start - 7)]
                    if contents in self._exec_stateful(')VARS')[3][0]:
                        contents = self._exec_stateful(f'{contents}')[3]
                        if len(contents) > 1:
                            contents = '\n'.join(contents)
                        else:
                            contents = contents[0]
                    end = text.find("'", start)
                    filepath = text[start:end]
                    flags = 0
                    if len(text) >= end + 2:
                        flags = int(text[end + 2])
                    if flags == 0:
                        with open(filepath, 'x') as f:
                            f.write(contents)
                    elif flags == 1:
                        with open(filepath, 'w') as f:
                            f.write(contents)
                    elif flags == 2:
                        with open(filepath, 'a') as f:
                            f.write(contents)
                    else:
                        raise Exception(f"Invalid flag: {flags}")
                    text = f"{len(contents)}"

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

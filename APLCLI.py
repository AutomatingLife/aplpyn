import json
from prompt_toolkit import PromptSession
from APLCompleter import APLCompleter
from prompt_toolkit.styles import style_from_pygments_cls
from prompt_toolkit.lexers import PygmentsLexer
from pygments.styles import get_style_by_name
from pygments.lexers import APLLexer


class APLCLI:
    def __init__(self, executor):
        self.executor = executor

    def run(self):
        codestyle = get_style_by_name('monokai')
        codestyle = style_from_pygments_cls(codestyle)
        completer = APLCompleter(self.executor.user_defs)
        session = PromptSession(completer=completer, lexer=PygmentsLexer(APLLexer), style=codestyle)
        print("APL CLI - type 'exit' to quit")
        while True:
            try:
                text = session.prompt('APL> ')
                if text.strip() == '⎕EXIT':
                    break
                if text.strip() == '⎕CLEAR' or text.strip() == ')CLEAR':
                    self.executor.clear()
                    self.executor.user_defs['functions'] = {}
                    self.executor.user_defs['variables'] = {}
                elif text.strip().startswith(')ERASE') or text.strip().startswith('⎕ERASE'):
                    start = text.find(')ERASE') + 7
                    end = len(text)
                    names = text[start:end].split()
                    for name in names:
                        if name in self.executor.user_defs['functions']:
                            del self.executor.user_defs['functions'][name]
                        if name in self.executor.user_defs['variables']:
                            del self.executor.user_defs['variables'][name]
                if '⎕EXPORT' in text:
                    start = text.find('⎕EXPORT') + 8
                    filepath = 'namespace.json'
                    self.executor.user_defs['state'] = self.executor.state
                    self.executor.user_defs['size'] = self.executor.size
                    self.executor.user_defs['hash'] = self.executor.hash
                    if "'" in text[start:]:
                        end = text.find("'", start)
                        filepath = text[start:end]
                    with open(filepath, 'w') as f:
                        f.write(json.dumps(self.executor.user_defs))
                    print(
                        f"{len(self.executor.user_defs['functions'])} functions {self.executor.user_defs['functions'].keys()} and {len(self.executor.user_defs['variables'])} variables {self.executor.user_defs['variables'].keys()} exported to {filepath}")
                    continue
                elif '⎕IMPORT' in text:
                    start = text.find('⎕IMPORT') + 8
                    filepath = 'namespace.json'
                    if "'" in text[start:]:
                        end = text.find("'", start)
                        filepath = text[start:end]
                    with open(filepath, 'r') as f:
                        namespace = json.loads(f.read())
                    self.executor.user_defs['functions'].update(namespace['functions'])
                    self.executor.user_defs['variables'].update(namespace['variables'])
                    self.executor.state = namespace['state']
                    self.executor.size = namespace['size']
                    self.executor.hash = namespace['hash']
                    print(
                        f"{len(self.executor.user_defs['functions'])} functions {self.executor.user_defs['functions'].keys()} and {len(self.executor.user_defs['variables'])} variables {self.executor.user_defs['variables'].keys()} imported from {filepath}")
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
                elif '⎕NPUT' in text:
                    start = text.find('⎕NPUT') + 6
                    contents = text[:(start - 7)]
                    if contents in self.executor.exec_stateful(')VARS')[3][0]:
                        contents = self.executor.exec_stateful(f'{contents}')[3]
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
                if '←' in text:
                    self.executor.store_definition(text)

                response = self.executor.exec_stateful(text)
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

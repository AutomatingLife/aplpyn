import json
from prompt_toolkit import PromptSession
from APLCompleter import APLCompleter

class APLCLI:
    def __init__(self, executor):
        self.executor = executor

    def run(self):
        completer = APLCompleter(self.executor.user_defs)
        session = PromptSession(completer=completer)
        print("APL CLI - type 'exit' to quit")
        while True:
            try:
                text = session.prompt('APL> ')
                if text.strip() == '⎕EXIT':
                    break
                if text.strip() == '⎕CLEAR':
                    self.executor.clear()
                    continue
                if '←' in text:
                    self.executor._store_definition(text)
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
                if '⎕IMPORT' in text:
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
                if '⎕NPUT' in text:
                    start = text.find('⎕NPUT') + 6
                    contents = text[:(start - 7)]
                    if contents in self.executor._exec_stateful(')VARS')[3][0]:
                        contents = self.executor._exec_stateful(f'{contents}')[3]
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

                response = self.executor._exec_stateful(text)
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
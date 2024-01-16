import json
import requests
class APLExecutor:
    def __init__(self):
        self.url = "https://tryapl.org/Exec"
        self.headers = {'Content-Type': 'application/json; charset=utf-8'}
        self.state = ''
        self.size = 0
        self.hash = ''
        self.user_defs = {'functions': {}, 'variables': {}, 'state': "", 'size': "", 'hash': ""}

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
        self.user_defs = {'functions': {}, 'variables': {}}

    def _store_definition(self, code):
        try:
            # Split the code at the assignment arrow
            name, definition = code.split('←', 1)
            name = name.strip()
            definition = definition.strip()
            comment = ''
            if '⍝' in definition:
                definition, comment = definition.split('⍝', 1)
                definition = definition.strip()
                comment = comment.strip()
            if definition.startswith('{') and definition.endswith('}'):
                self.user_defs['functions'][name] = {
                    'source': definition.strip(),
                    'comment': comment or definition if len(definition) <= 50 else 'User Defined Function'
                }

            else:
                self.user_defs['variables'][name] = {
                    'source': definition.strip(),
                    'comment': comment or definition if len(definition) <= 50 else 'User Defined Variable'
                }
        except Exception as e:
            print(f"An error occurred: {e}")
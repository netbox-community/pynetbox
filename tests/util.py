import json


class Response(object):
    def __init__(self, fixture=None, status_code=200, ok=True, content=None):
        self.status_code = status_code
        self.content = json.dumps(content) if content else self.load_fixture(fixture)
        self.ok = ok

    def load_fixture(self, path):
        with open("tests/fixtures/{}".format(path), 'r') as f:
            return f.read()

    def json(self):
        return json.loads(self.content)

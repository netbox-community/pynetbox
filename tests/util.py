import json
from unittest.mock import Mock


class Response(object):
    def __init__(self, fixture=None, status_code=200, ok=True, content=None):
        self.status_code = status_code
        self.content = json.dumps(content) if content else self.load_fixture(fixture)
        self.request = Mock()
        self.request.body = ""
        self.url = "http://localhost:8000/"
        self.ok = ok

    def load_fixture(self, path):
        if not path:
            return ""
        with open("tests/fixtures/{}".format(path), "r") as f:
            return f.read()

    def json(self):
        return json.loads(self.content)

class Response:
    def __init__(self, fixture=None, status_code=200, ok=True):
        self.status_code = status_code
        self.content = self.load_fixture(fixture)
        self.ok = ok
        self.text = self.content

    def load_fixture(self, path):
        with open("tests/fixtures/{}".format(path), 'r') as f:
            return f.read()

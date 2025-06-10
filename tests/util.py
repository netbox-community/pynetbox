import json


class Response:
    def __init__(self, fixture=None, status_code=200, ok=True, content=None):
        self.status_code = status_code
        self.content = json.dumps(content) if content else self.load_fixture(fixture)
        self.ok = ok
        self.headers = {"API-Version":'3.1'}

    def load_fixture(self, path):
        if not path:
            return "{}"
        with open("tests/fixtures/{}".format(path), "r") as f:
            return f.read()

    def json(self):
        return json.loads(self.content)

def openapi_mock():
    """Mock function to simulate Api.openapi()
    """
    return {
        "paths": {
            "/api/test/test/" : {
                "get" : {
                    "parameters" :[
                        {"name":"test"},
                        {"name":"name"},
                    ]
                },
            },
        },
    }
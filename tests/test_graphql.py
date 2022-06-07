from os import path

import pytest
import requests_mock
from pynetbox.core.api import Api
from pynetbox.core.graphql import GraphQLRecord, GraphQLException

HERE = path.abspath(path.dirname(__file__))


def load_api_calls(mock, api_calls):
    for api_call in api_calls:
        with open(api_call["fixture_path"], "r") as f:
            api_call["text"] = f.read()

        mock.request(
            method=api_call["method"],
            url=api_call["url"],
            text=api_call["text"],
            status_code=api_call["status_code"],
            complete_qs=True,
        )


def test_setup(graphql_test_class):
    assert isinstance(graphql_test_class.api, Api)


# Test that everything works with a basic string
def test_get_basic_string(graphql_test_class):
    query_str = """
query {
  devices {
    name
    id
    primary_ip4 {
        address
    }
  }
}
"""
    api_calls = [
        {
            "fixture_path": f"{HERE}/fixtures/graphql/01_get_devices.json",
            "url": "https://mocknetbox.example.com/graphql/",
            "method": "post",
            "status_code": 200,
        }
    ]
    expected_response = {
        "data": {
            "devices": [
                {"name": "grb-rtr01", "id": 1, "primary_ip4": {"address": "192.0.2.10/32"}},
                {"name": "msp-rtr01", "id": 2, "primary_ip4": {"address": "192.0.2.11/32"}},
                {"name": "msp-rtr02", "id": 4, "primary_ip4": {"address": "192.0.2.12/32"}},
            ]
        }
    }
    with requests_mock.Mocker() as mock:
        load_api_calls(mock, api_calls)
        query_result = graphql_test_class.query(query=query_str, variables=None)
        assert isinstance(query_result, GraphQLRecord)
        assert query_result.json == expected_response
        assert query_result.status_code == 200


# Verify result with an ID passed in
def test_get_string_with_id(graphql_test_class):
    query_str = """
query {
  devices(id: 1) {
    name
    id
    primary_ip4 {
        address
    }
  }
}
"""
    api_calls = [
        {
            "fixture_path": f"{HERE}/fixtures/graphql/03_get_device_with_id.json",
            "url": "https://mocknetbox.example.com/graphql/",
            "method": "post",
            "status_code": 200,
        }
    ]
    expected_response = {
        "data": {"devices": [{"name": "grb-rtr01", "id": 1, "primary_ip4": {"address": "192.0.2.10/32"}}]}
    }
    with requests_mock.Mocker() as mock:
        load_api_calls(mock, api_calls)
        query_result = graphql_test_class.query(query=query_str, variables=None)

    assert isinstance(query_result, GraphQLRecord)
    assert query_result.json == expected_response
    assert query_result.status_code == 200


# Test if query is not a string that it fails
def test_get_invalid_query_data(graphql_test_class):
    query_str = ["hello"]
    api_calls = [
        {
            "fixture_path": f"{HERE}/fixtures/graphql/02_get_wrong_query.json",
            "url": "https://mocknetbox.example.com/graphql/",
            "method": "post",
            "status_code": 400,
        }
    ]
    expected_response = {}
    with requests_mock.Mocker() as mock:
        load_api_calls(mock, api_calls)
        with pytest.raises(TypeError) as err:
            graphql_test_class.query(query=query_str, variables=None) == expected_response

        assert str(err.value) == "Query should be of type string, not of type <class 'list'>"


# Verify no result query is empty
def test_get_id_no_result(graphql_test_class):
    query_str = """
query {
  devices(id: 12) {
    name
    id
    primary_ip4 {
        address
    }
  }
}
"""
    api_calls = [
        {
            "fixture_path": f"{HERE}/fixtures/graphql/04_no_devices.json",
            "url": "https://mocknetbox.example.com/graphql/",
            "method": "post",
            "status_code": 200,
        }
    ]
    expected_response = {"data": {"devices": []}}
    with requests_mock.Mocker() as mock:
        load_api_calls(mock, api_calls)
        query_result = graphql_test_class.query(query=query_str, variables=None)

    assert isinstance(query_result, GraphQLRecord)
    assert query_result.json == expected_response
    assert query_result.status_code == 200


# Test passing a variable in works
def test_get_string_with_variables(graphql_test_class):
    query_str = """
query ($device: String!) {
  devices(name: $device) {
    name
    id
    primary_ip4 {
        address
    }
  }
}
"""
    variables = {"device": "grb-rtr01"}
    api_calls = [
        {
            "fixture_path": f"{HERE}/fixtures/graphql/05_get_device_filtered_by_name.json",
            "url": "https://mocknetbox.example.com/graphql/",
            "method": "post",
            "status_code": 200,
        }
    ]
    expected_response = {
        "data": {"devices": [{"name": "grb-rtr01", "id": 1, "primary_ip4": {"address": "192.0.2.10/32"}}]}
    }
    with requests_mock.Mocker() as mock:
        load_api_calls(mock, api_calls)
        query_result = graphql_test_class.query(query=query_str, variables=variables)

    assert isinstance(query_result, GraphQLRecord)
    assert query_result.json == expected_response
    assert query_result.status_code == 200


# Test variable error in format
def test_get_string_with_incorrect_variables_datatype(graphql_test_class):
    query_str = """
query ($device: String!) {
  devices(name: $device) {
    name
    id
    primary_ip4 {
        address
    }
  }
}
"""
    variables = {"device", "grb-rtr01"}
    api_calls = [
        {
            "fixture_path": f"{HERE}/fixtures/graphql/05_get_device_filtered_by_name.json",
            "url": "https://mocknetbox.example.com/graphql/",
            "method": "post",
            "status_code": 200,
        }
    ]
    expected_response = {
        "data": {"devices": [{"name": "grb-rtr01", "id": 1, "primary_ip4": {"address": "192.0.2.10/32"}}]}
    }
    with requests_mock.Mocker() as mock:
        load_api_calls(mock, api_calls)
        with pytest.raises(TypeError) as err:
            graphql_test_class.query(query=query_str, variables=variables)

        assert str(err.value) == "Variables should be of type dictionary, not of type <class 'set'>"


# Test variable no result
def test_get_string_with_variables_no_result(graphql_test_class):
    query_str = """
query ($device: String!) {
  devices(name: $device) {
    name
    id
    primary_ip4 {
        address
    }
  }
}
"""
    variables = {"device": "gr-rtr01"}
    api_calls = [
        {
            "fixture_path": f"{HERE}/fixtures/graphql/04_no_devices.json",
            "url": "https://mocknetbox.example.com/graphql/",
            "method": "post",
            "status_code": 200,
        }
    ]
    expected_response = {"data": {"devices": []}}
    with requests_mock.Mocker() as mock:
        load_api_calls(mock, api_calls)
        query_result = graphql_test_class.query(query=query_str, variables=None)

    assert isinstance(query_result, GraphQLRecord)
    assert query_result.json == expected_response
    assert query_result.status_code == 200


# Verify that incorrect data that is passed in that there is an error raised
def test_get_invalid_query_string(graphql_test_class):
    query_str = """
query {
  test {
    name
    id
    primary_ip4 {
      address
    }
  }
}
"""
    api_calls = [
        {
            "fixture_path": f"{HERE}/fixtures/graphql/02_get_wrong_query.json",
            "url": "https://mocknetbox.example.com/graphql/",
            "method": "post",
            "status_code": 400,
        }
    ]
    expected_errors = [
        {
            "message": 'Cannot query field "test" on type "Query". Did you mean "tenant"?',
            "locations": [{"line": 2, "column": 3}],
        }
    ]
    expected_response = {
        "errors": [
            {
                "message": 'Cannot query field "test" on type "Query". Did you mean "tenant"?',
                "locations": [{"line": 2, "column": 3}],
            }
        ]
    }
    with requests_mock.Mocker() as mock:
        load_api_calls(mock, api_calls)
        with pytest.raises(GraphQLException) as err:
            graphql_test_class.query(query=query_str, variables=None)

    assert isinstance(err.value, GraphQLException)
    assert err.value.status_code == 400
    assert err.value.errors == expected_errors
    assert err.value.url == "https://mocknetbox.example.com/graphql/"
    assert (
        err.value.body
        == b'{"query": "\\nquery {\\n  test {\\n    name\\n    id\\n    primary_ip4 {\\n      address\\n    }\\n  }\\n}\\n", "variables": null}'
    )
    assert err.value.reason == None
    assert err.value.json == expected_response


# Test Multiple errors
def test_get_multiple_invalid_query_string(graphql_test_class):
    query_str = """
query {
  devices {
    nae
    id
    primary_ip4 {
        address
    }
  }
  sites {
    nme
    id
  }
}
"""
    api_calls = [
        {
            "fixture_path": f"{HERE}/fixtures/graphql/06_get_multiple_wrong_query.json",
            "url": "https://mocknetbox.example.com/graphql/",
            "method": "post",
            "status_code": 400,
        }
    ]
    expected_errors = [
        {
            "message": 'Cannot query field "nae" on type "DeviceType". Did you mean "name" or "face"?',
            "locations": [{"line": 3, "column": 5}],
        },
        {
            "message": 'Cannot query field "nme" on type "SiteType". Did you mean "name"?',
            "locations": [{"line": 10, "column": 5}],
        },
    ]
    expected_response = {
        "errors": [
            {
                "message": 'Cannot query field "nae" on type "DeviceType". Did you mean "name" or "face"?',
                "locations": [{"line": 3, "column": 5}],
            },
            {
                "message": 'Cannot query field "nme" on type "SiteType". Did you mean "name"?',
                "locations": [{"line": 10, "column": 5}],
            },
        ]
    }
    with requests_mock.Mocker() as mock:
        load_api_calls(mock, api_calls)
        with pytest.raises(GraphQLException) as err:
            graphql_test_class.query(query=query_str, variables=None)

    assert isinstance(err.value, GraphQLException)
    assert err.value.status_code == 400
    assert err.value.errors == expected_errors
    assert err.value.url == "https://mocknetbox.example.com/graphql/"
    assert err.value.body == (
        b'{"query": "\\nquery {\\n  devices {\\n    nae\\n    id\\n    primary_ip4 {\\n        address\\n    }\\n  }\\n  sites {\\n    nme\\n    id\\n  }\\n}\\n", "variables": null}'
    )
    assert err.value.reason == None
    assert err.value.json == expected_response

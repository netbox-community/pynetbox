"""
(c) 2017 DigitalOcean

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
try:
    import concurrent.futures as cf
except ImportError:
    pass
import json
from six.moves.urllib.parse import urlencode


def calc_pages(limit, count):
    """Calculate number of pages required for full results set."""
    return int(count / limit) + (limit % count > 0)


class RequestError(Exception):
    """Basic Request Exception

    More detailed exception that returns the original requests object
    for inspection. Along with some attributes with specific details
    from the requests object. If return is json we decode and add it
    to the message.

    :Example:

    >>> try:
    ...   nb.dcim.devices.create(name="destined-for-failure")
    ... except pynetbox.RequestError as e:
    ...   print(e.error)

    """

    def __init__(self, req):
        if req.status_code == 404:
            self.message = "The requested url: {} could not be found.".format(req.url)
        else:
            try:
                self.message = "The request failed with code {} {}: {}".format(
                    req.status_code, req.reason, req.json()
                )
            except ValueError:
                self.message = (
                    "The request failed with code {} {} but more specific "
                    "details were not returned in json. Check the NetBox Logs "
                    "or investigate this exception's error attribute.".format(
                        req.status_code, req.reason
                    )
                )

        super(RequestError, self).__init__(req)
        self.req = req
        self.request_body = req.request.body
        self.base = req.url
        self.error = req.text

    def __str__(self):
        return self.message


class AllocationError(Exception):
    """Allocation Exception

    Used with available-ips/available-prefixes when there is no
    room for allocation and NetBox returns 204 No Content (before
    NetBox 3.1.1) or 409 Conflict (since NetBox 3.1.1+).
    """

    def __init__(self, req):
        super(AllocationError, self).__init__(req)
        self.req = req
        self.request_body = req.request.body
        self.base = req.url
        self.error = "The requested allocation could not be fulfilled."

    def __str__(self):
        return self.error


class ContentError(Exception):
    """Content Exception

    If the API URL does not point to a valid NetBox API, the server may
    return a valid response code, but the content is not json. This
    exception is raised in those cases.
    """

    def __init__(self, req):
        super(ContentError, self).__init__(req)
        self.req = req
        self.request_body = req.request.body
        self.base = req.url
        self.error = (
            "The server returned invalid (non-json) data. Maybe not a NetBox server?"
        )

    def __str__(self):
        return self.error


class Request(object):
    """Creates requests to the Netbox API

    Responsible for building the url and making the HTTP(S) requests to
    Netbox's API

    :param base: (str) Base URL passed in api() instantiation.
    :param filters: (dict, optional) contains key/value pairs that
        correlate to the filters a given endpoint accepts.
        In (e.g. /api/dcim/devices/?name='test') 'name': 'test'
        would be in the filters dict.
    :param private_key: (str, optional) The user's private key as a
        string.
    """

    def __init__(
        self,
        base,
        http_session,
        filters=None,
        limit=None,
        offset=None,
        key=None,
        token=None,
        private_key=None,
        session_key=None,
        threading=False,
    ):
        """
        Instantiates a new Request object

        Args:
            base (string): Base URL passed in api() instantiation.
            filters (dict, optional): contains key/value pairs that
                correlate to the filters a given endpoint accepts.
                In (e.g. /api/dcim/devices/?name='test') 'name': 'test'
                would be in the filters dict.
            key (int, optional): database id of the item being queried.
            private_key (string, optional): The user's private key as a
                string.
        """
        self.base = self.normalize_url(base)
        self.filters = filters or None
        self.key = key
        self.token = token
        self.private_key = private_key
        self.session_key = session_key
        self.http_session = http_session
        self.url = self.base if not key else "{}{}/".format(self.base, key)
        self.threading = threading
        self.limit = limit
        self.offset = offset

    def get_openapi(self):
        """Gets the OpenAPI Spec"""
        headers = {
            "Content-Type": "application/json;",
        }
        req = self.http_session.get(
            "{}docs/?format=openapi".format(self.normalize_url(self.base)),
            headers=headers,
        )
        if req.ok:
            return req.json()
        else:
            raise RequestError(req)

    def get_version(self):
        """Gets the API version of NetBox.

        Issues a GET request to the base URL to read the API version from the
        response headers.

        :Raises: RequestError if req.ok returns false.
        :Returns: Version number as a string. Empty string if version is not
        present in the headers.
        """
        headers = {
            "Content-Type": "application/json;",
        }
        req = self.http_session.get(
            self.normalize_url(self.base),
            headers=headers,
        )
        if req.ok:
            return req.headers.get("API-Version", "")
        else:
            raise RequestError(req)

    def get_session_key(self):
        """Requests session key

        Issues a GET request to the `get-session-key` endpoint for
        subsequent use in requests from the `secrets` endpoint.

        :Returns: String containing session key.
        """
        req = self.http_session.post(
            "{}secrets/get-session-key/?preserve_key=True".format(self.base),
            headers={
                "accept": "application/json",
                "authorization": "Token {}".format(self.token),
                "Content-Type": "application/x-www-form-urlencoded",
            },
            data=urlencode({"private_key": self.private_key.strip("\n")}),
        )
        if req.ok:
            try:
                return req.json()["session_key"]
            except json.JSONDecodeError:
                raise ContentError(req)
        else:
            raise RequestError(req)

    def get_status(self):
        """Gets the status from /api/status/ endpoint in NetBox.

        :Returns: Dictionary as returned by NetBox.
        :Raises: RequestError if request is not successful.
        """
        headers = {"Content-Type": "application/json;"}
        if self.token:
            headers["authorization"] = "Token {}".format(self.token)
        req = self.http_session.get(
            "{}status/".format(self.normalize_url(self.base)),
            headers=headers,
        )
        if req.ok:
            return req.json()
        else:
            raise RequestError(req)

    def normalize_url(self, url):
        """Builds a url for POST actions."""
        if url[-1] != "/":
            return "{}/".format(url)

        return url

    def _make_call(self, verb="get", url_override=None, add_params=None, data=None):
        if verb in ("post", "put") or verb == "delete" and data:
            headers = {"Content-Type": "application/json;"}
        else:
            headers = {"accept": "application/json;"}

        if self.token:
            headers["authorization"] = "Token {}".format(self.token)
        if self.session_key:
            headers["X-Session-Key"] = self.session_key

        params = {}
        if not url_override:
            if self.filters:
                params.update(self.filters)
            if add_params:
                params.update(add_params)

        req = getattr(self.http_session, verb)(
            url_override or self.url, headers=headers, params=params, json=data
        )

        if req.status_code in [204, 409] and verb == "post":
            raise AllocationError(req)
        if verb == "delete":
            if req.ok:
                return True
            else:
                raise RequestError(req)
        elif req.ok:
            try:
                return req.json()
            except json.JSONDecodeError:
                raise ContentError(req)
        else:
            raise RequestError(req)

    def concurrent_get(self, ret, page_size, page_offsets):
        futures_to_results = []
        with cf.ThreadPoolExecutor(max_workers=4) as pool:
            for offset in page_offsets:
                new_params = {"offset": offset, "limit": page_size}
                futures_to_results.append(
                    pool.submit(self._make_call, add_params=new_params)
                )

            for future in cf.as_completed(futures_to_results):
                result = future.result()
                ret.extend(result["results"])

    def get(self, add_params=None):
        """Makes a GET request.

        Makes a GET request to NetBox's API, and automatically recurses
        any paginated results.

        :raises: RequestError if req.ok returns false.
        :raises: ContentError if response is not json.

        :Returns: List of `Response` objects returned from the
            endpoint.
        """

        if not add_params and self.limit is not None:
            add_params = {"limit": self.limit}
            if self.limit and self.offset is not None:
                # if non-zero limit and some offset -> add offset
                add_params["offset"] = self.offset
        req = self._make_call(add_params=add_params)
        if isinstance(req, dict) and req.get("results") is not None:
            self.count = req["count"]
            if self.offset is not None:
                # only yield requested page results if paginating
                for i in req["results"]:
                    yield i
            elif self.threading:
                ret = req["results"]
                if req.get("next"):
                    page_size = len(req["results"])
                    pages = calc_pages(page_size, req["count"])
                    page_offsets = [
                        increment * page_size for increment in range(1, pages)
                    ]
                    if pages == 1:
                        req = self._make_call(url_override=req.get("next"))
                        ret.extend(req["results"])
                    else:
                        self.concurrent_get(ret, page_size, page_offsets)
                for i in ret:
                    yield i
            else:
                first_run = True
                for i in req["results"]:
                    yield i
                while req["next"]:
                    # Not worrying about making sure add_params kwargs is
                    # passed in here because results from detail routes aren't
                    # paginated, thus far.
                    if first_run:
                        req = self._make_call(
                            add_params={
                                "limit": self.limit or req["count"],
                                "offset": len(req["results"]),
                            }
                        )
                    else:
                        req = self._make_call(url_override=req["next"])
                    first_run = False
                    for i in req["results"]:
                        yield i
        elif isinstance(req, list):
            self.count = len(req)
            for i in req:
                yield i
        else:
            self.count = len(req)
            yield req

    def put(self, data):
        """Makes PUT request.

        Makes a PUT request to NetBox's API. Adds the session key to
        headers if the `private_key` attribute was populated.

        :param data: (dict) Contains a dict that will be turned into a
            json object and sent to the API.
        :raises: RequestError if req.ok returns false.
        :raises: ContentError if response is not json.
        :returns: Dict containing the response from NetBox's API.
        """
        return self._make_call(verb="put", data=data)

    def post(self, data):
        """Makes POST request.

        Makes a POST request to NetBox's API. Adds the session key to
        headers if the `private_key` attribute was populated.

        :param data: (dict) Contains a dict that will be turned into a
            json object and sent to the API.
        :raises: RequestError if req.ok returns false.
        :raises: AllocationError if req.status_code is 204 (No Content)
            as with available-ips and available-prefixes when there is
            no room for the requested allocation.
        :raises: ContentError if response is not json.
        :Returns: Dict containing the response from NetBox's API.
        """
        return self._make_call(verb="post", data=data)

    def delete(self, data=None):
        """Makes DELETE request.

        Makes a DELETE request to NetBox's API.

        :param data: (list) Contains a dict that will be turned into a
            json object and sent to the API.
        Returns:
            True if successful.

        Raises:
            RequestError if req.ok doesn't return True.
        """
        return self._make_call(verb="delete", data=data)

    def patch(self, data):
        """Makes PATCH request.

        Makes a PATCH request to NetBox's API.

        :param data: (dict) Contains a dict that will be turned into a
            json object and sent to the API.
        :raises: RequestError if req.ok returns false.
        :raises: ContentError if response is not json.
        :returns: Dict containing the response from NetBox's API.
        """
        return self._make_call(verb="patch", data=data)

    def options(self):
        """Makes an OPTIONS request.

        Makes an OPTIONS request to NetBox's API.

        :raises: RequestError if req.ok returns false.
        :raises: ContentError if response is not json.

        :returns: Dict containing the response from NetBox's API.
        """
        return self._make_call(verb="options")

    def get_count(self, *args, **kwargs):
        """Returns object count for query

        Makes a query to the endpoint with ``limit=1`` set and only
        returns the value of the "count" field.

        :raises: RequestError if req.ok returns false.
        :raises: ContentError if response is not json.

        :returns: Int of number of objects query returned.
        """

        if not hasattr(self, "count"):
            self.count = self._make_call(add_params={"limit": 1})["count"]
        return self.count

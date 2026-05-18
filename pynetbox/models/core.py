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

from pynetbox.core.endpoint import DetailEndpoint
from pynetbox.core.response import JsonField, Record


class DataSources(Record):
    @property
    def sync(self):
        """Represents the ``sync`` detail endpoint.

        Returns a DetailEndpoint object that is the interface for
        triggering a sync of the data source.

        ## Returns
        DetailEndpoint object.

        ## Examples

        ```python
        data_source = nb.core.data_sources.get(123)
        data_source.sync.create()
        ```
        """
        return DetailEndpoint(self, "sync")


class Jobs(Record):
    pass


class ObjectChanges(Record):
    object_data = JsonField
    postchange_data = JsonField
    prechange_data = JsonField

    def __str__(self):
        return self.request_id

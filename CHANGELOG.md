
v4.0.8 (2019-09-27)

* [#165](https://github.com/digitalocean/pynetbox/issues/165) - Returns ContentError when 2XX response but not JSON.

---

v4.0.7 (2019-09-13)

## Bug Fixes

* [#156](https://github.com/digitalocean/pynetbox/issues/156) - Returns AllocationError when NetBox responds with a 204 to Allocation requests (Thanks @markkuleinio).
* [#152](https://github.com/digitalocean/pynetbox/issues/152) - Makes App object pickleable (Thanks @xtelinco and @kartiksubbarao for testing).

---

v4.0.6 (2018-12-29)

## Bug Fixes
* [#137](https://github.com/digitalocean/pynetbox/issues/137) - Fixes behavior where appending an existing VLAN object id to tagged_vlans would cause .save() to still trigger a PATCH operation.

---

v4.0.5 (2018-12-14)

## Bug Fixes
* [#132](https://github.com/digitalocean/pynetbox/pull/132) - Fixes list comparison issue in `Record._diff`. 
* [#134](https://github.com/digitalocean/pynetbox/issues/134) - Returns None from Endpoint.get() when no items are found instead of empty list from `.filter()`.

---
v4.0.4 (2018-12-07)

## Bug Fixes
* Fixes IndexError introduced by fix for #127 when field is empty list.

---
v4.0.3 (2018-12-07)

## Bug Fixes
* [#127](https://github.com/digitalocean/pynetbox/issues/127) - Fixes `__iter__` method on Record object so that it properly return lists record objects. Like tagged_vlans on for Interfaces.

---

v4.0.2 (2018-12-06)

## Bug Fixes
* [#126](https://github.com/digitalocean/pynetbox/issues/126) - Fixes TypeError when calling save on interfaces Record with tagged_vlans.

---

v4.0.1 (2018-12-06)

## Bug Fixes
* [#122](https://github.com/digitalocean/pynetbox/issues/122) - Adds missing authentication credentials for `.choices()`.


---

v4.0.0 (2018-12-04)

## Enhancements

* [#109](https://github.com/digitalocean/pynetbox/issues/109) - Clean up tests a bit.
* Added cable endpoint support coming in NetBox 2.5.
* Added some detail to the ValueError raised when `.get()` returns more than one object.
* Added reserved kwargs to `.get()` and `.filter()` ("id", "pk", "limit", "offset").
* Made RequestError more verbose when the NetBox API returns a json response. Also added more details when a 404 is returned (e.g. misspelled endpoints). 

## API Changes

* [#22](https://github.com/digitalocean/pynetbox/issues/22) - Switch to using PATCH instead of PUTs for updates. Also added an `.update()` method to Response objects that takes a dictionary to update multiple values on the object.
* [#24](https://github.com/digitalocean/pynetbox/issues/24) - Add basic support for the `_choices` endpoint on each app by adding a `choices()` method to the App object.
* [#108](https://github.com/digitalocean/pynetbox/issues/108) - Return `Record` objects from `.create()`.

## Bug Fixes

* [#88](https://github.com/digitalocean/pynetbox/issues/88) - Raise an exception now if `.filter()` is passed no kwargs.
* [#90](https://github.com/digitalocean/pynetbox/issues/90) - Fixes some miscellaneous issues related to converting certain Record object's fields into netaddr.IPNetwork objects. That feature has been removed and it simply return strings now.

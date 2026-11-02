import pytest


def raw(value):
    """Return the raw selection value, whether NetBox sent it bare or as {value, label}."""
    if isinstance(value, dict):
        return value["value"]
    if isinstance(value, list):
        return [raw(v) for v in value]
    return value


@pytest.fixture(scope="module")
def choice_set(api):
    choice_set = api.extras.custom_field_choice_sets.create(
        name="pynetbox-806",
        extra_choices=[["a", "A"], ["b", "B"], ["c", "C"]],
    )
    yield choice_set
    choice_set.delete()


@pytest.fixture(scope="module")
def custom_fields(api, choice_set):
    custom_fields = [
        api.extras.custom_fields.create(
            name=name,
            type=cf_type,
            object_types=["dcim.site"],
            **extra,
        )
        for name, cf_type, extra in (
            ("cf_806_select", "select", {"choice_set": choice_set.id}),
            ("cf_806_multiselect", "multiselect", {"choice_set": choice_set.id}),
            ("cf_806_json", "json", {}),
            ("cf_806_text", "text", {}),
        )
    ]
    yield
    for custom_field in custom_fields:
        custom_field.delete()


@pytest.fixture
def cf_site(api, custom_fields):
    site = api.dcim.sites.create(
        name="test-cf-806",
        slug="test-cf-806",
        custom_fields={
            "cf_806_select": "a",
            "cf_806_multiselect": ["a", "b"],
            "cf_806_json": {"value": 5, "label": "five"},
            "cf_806_text": "foo",
        },
    )
    yield api.dcim.sites.get(site.id)
    site.delete()


class TestCustomFieldSave:
    """Regression tests for issue #806: saving a record must not send untouched
    custom fields back in the shape NetBox returned them."""

    def test_edit_one_custom_field_keeps_the_others(self, api, cf_site):
        cf_site.custom_fields["cf_806_text"] = "bar"
        assert cf_site.save()

        custom_fields = api.dcim.sites.get(cf_site.id).custom_fields
        assert raw(custom_fields["cf_806_select"]) == "a"
        assert raw(custom_fields["cf_806_multiselect"]) == ["a", "b"]
        assert custom_fields["cf_806_json"] == {"value": 5, "label": "five"}
        assert custom_fields["cf_806_text"] == "bar"

    def test_in_place_multiselect_edit(self, api, cf_site):
        cf_site.custom_fields["cf_806_multiselect"].append("c")
        assert cf_site.save()

        custom_fields = api.dcim.sites.get(cf_site.id).custom_fields
        assert raw(custom_fields["cf_806_multiselect"]) == ["a", "b", "c"]

    def test_copied_selection_value(self, api, cf_site):
        cf_site.custom_fields["cf_806_select"] = {"value": "b", "label": "B"}
        assert cf_site.save()

        custom_fields = api.dcim.sites.get(cf_site.id).custom_fields
        assert raw(custom_fields["cf_806_select"]) == "b"

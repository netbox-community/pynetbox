import pytest
from packaging import version

import pynetbox


@pytest.fixture(scope="module")
def rack(api, site):
    rack = api.dcim.racks.create(site=site.id, name="test-rack")
    yield rack
    rack.delete()


@pytest.fixture(scope="module")
def device(api, site, device_type, device_role):
    device = api.dcim.devices.create(
        name="test-device",
        device_role=device_role.id,
        device_type=device_type.id,
        site=site.id,
        color="000000",
    )
    yield device
    device.delete()


@pytest.mark.usefixtures("init")
class BaseTest:
    app = "dcim"

    def _init_helper(
        self,
        request,
        fixture,
        update_field=None,
        filter_kwargs=None,
        endpoint=None,
        str_repr=None,
    ):
        request.cls.endpoint = endpoint
        request.cls.fixture = fixture
        request.cls.update_field = update_field
        request.cls.filter_kwargs = filter_kwargs
        request.cls.str_repr = str_repr

    def test_create(self):
        assert self.fixture

    def test_str(self):
        if self.str_repr:
            test = str(self.fixture)
            assert test == self.str_repr

    def test_update_fixture(self):
        if self.update_field:
            setattr(self.fixture, self.update_field, "Test Value")
            assert self.fixture.save()

    def test_get_fixture_by_id(self, api):
        test = getattr(getattr(api, self.app), self.endpoint).get(self.fixture.id)
        assert test
        if self.update_field:
            assert getattr(test, self.update_field) == "Test Value"

    def test_get_fixture_by_kwarg(self, api):
        test = getattr(getattr(api, self.app), self.endpoint).get(**self.filter_kwargs)
        assert test
        if self.update_field:
            assert getattr(test, self.update_field) == "Test Value"

    def test_filter_fixture(self, api):
        test = list(
            getattr(getattr(api, self.app), self.endpoint).filter(**self.filter_kwargs)
        )[0]
        assert test
        if self.update_field:
            assert getattr(test, self.update_field) == "Test Value"


class TestSite(BaseTest):
    @pytest.fixture(scope="class")
    def init(self, request, site):
        self._init_helper(
            request,
            site,
            filter_kwargs={"name": "test"},
            update_field="description",
            endpoint="sites",
        )

    @pytest.fixture(scope="class")
    def add_sites(self, api):
        sites = api.dcim.sites.create(
            [
                {"name": "test{}".format(i), "slug": "test{}".format(i)}
                for i in range(2, 20)
            ]
        )
        yield
        for i in sites:
            i.delete()

    def test_threading_duplicates(self, docker_netbox_service, add_sites):
        api = pynetbox.api(
            docker_netbox_service["url"],
            token="0123456789abcdef0123456789abcdef01234567",
            threading=True,
        )
        test = api.dcim.sites.all(limit=5)
        test_list = list(test)
        test_set = set(test_list)
        assert len(test_list) == len(test_set)


class TestRack(BaseTest):
    @pytest.fixture(scope="class")
    def init(self, request, rack):
        self._init_helper(
            request,
            rack,
            filter_kwargs={"name": rack.name},
            update_field="comments",
            endpoint="racks",
        )

    def test_get_elevation(self):
        test = self.fixture.elevation.list()
        assert test
        assert isinstance(test, list)


class TestManufacturer(BaseTest):
    @pytest.fixture(scope="class")
    def init(self, request, manufacturer, nb_version):
        self._init_helper(
            request,
            manufacturer,
            filter_kwargs={"name": manufacturer.name},
            update_field="description" if version.parse("2.10") < nb_version else None,
            endpoint="manufacturers",
        )


class TestDeviceType(BaseTest):
    @pytest.fixture(scope="class")
    def init(self, request, device_type):
        self._init_helper(
            request,
            device_type,
            filter_kwargs={"model": device_type.model},
            update_field="comments",
            endpoint="device_types",
            str_repr=device_type.model,
        )


class TestDevice(BaseTest):
    @pytest.fixture(scope="class")
    def init(self, request, device):
        self._init_helper(
            request,
            device,
            filter_kwargs={"name": device.name},
            update_field="comments",
            endpoint="devices",
        )


class TestInterface(BaseTest):
    @pytest.fixture(scope="class")
    def interface(self, api, device):
        ret = api.dcim.interfaces.create(
            name="test-interface", type="1000base-t", device=device.id
        )
        yield ret
        ret.delete()

    @pytest.fixture(scope="class")
    def init(self, request, interface):
        self._init_helper(
            request,
            interface,
            filter_kwargs={"name": interface.name},
            update_field="description",
            endpoint="interfaces",
        )


class TestPowerCable(BaseTest):
    @pytest.fixture(scope="class")
    def power_outlet(self, api, device_type, device_role, site):
        pdu = api.dcim.devices.create(
            name="test-pdu",
            device_role=device_role.id,
            device_type=device_type.id,
            site=site.id,
        )
        outlet = api.dcim.power_outlets.create(name="outlet", device=pdu.id)
        yield outlet
        pdu.delete()

    @pytest.fixture(scope="class")
    def power_port(self, api, device):
        ret = api.dcim.power_ports.create(name="PSU1", device=device.id)
        yield ret

    @pytest.fixture(scope="class")
    def power_cable(self, api, power_outlet, power_port):
        cable = api.dcim.cables.create(
            termination_a_id=power_port.id,
            termination_a_type="dcim.powerport",
            termination_b_id=power_outlet.id,
            termination_b_type="dcim.poweroutlet",
        )
        yield cable
        cable.delete()

    @pytest.fixture(scope="class")
    def init(self, request, power_cable):
        self._init_helper(
            request,
            power_cable,
            filter_kwargs={"id": power_cable.id},
            endpoint="cables",
            str_repr="PSU1 <> outlet",
        )


class TestConsoleCable(BaseTest):
    @pytest.fixture(scope="class")
    def console_server_port(self, api, device_type, device_role, site):
        device = api.dcim.devices.create(
            name="test-console-server",
            device_role=device_role.id,
            device_type=device_type.id,
            site=site.id,
        )
        ret = api.dcim.console_server_ports.create(name="Port 1", device=device.id)
        yield ret
        device.delete()

    @pytest.fixture(scope="class")
    def console_port(self, api, device):
        ret = api.dcim.console_ports.create(name="Console", device=device.id)
        yield ret

    @pytest.fixture(scope="class")
    def console_cable(self, api, console_port, console_server_port):
        ret = api.dcim.cables.create(
            termination_a_id=console_port.id,
            termination_a_type="dcim.consoleport",
            termination_b_id=console_server_port.id,
            termination_b_type="dcim.consoleserverport",
        )
        yield ret
        ret.delete()

    @pytest.fixture(scope="class")
    def init(self, request, console_cable):
        self._init_helper(
            request,
            console_cable,
            filter_kwargs={"id": console_cable.id},
            endpoint="cables",
            str_repr="Console <> Port 1",
        )


class TestInterfaceCable(BaseTest):
    @pytest.fixture(scope="class")
    def interface_b(self, api, device_type, device_role, site):
        device = api.dcim.devices.create(
            name="test-device-2",
            device_role=device_role.id,
            device_type=device_type.id,
            site=site.id,
        )
        ret = api.dcim.interfaces.create(
            name="Ethernet1", type="1000base-t", device=device.id
        )
        yield ret
        device.delete()

    @pytest.fixture(scope="class")
    def interface_a(self, api, device):
        ret = api.dcim.interfaces.create(
            name="Ethernet1", type="1000base-t", device=device.id
        )
        yield ret

    @pytest.fixture(scope="class")
    def interface_cable(self, api, interface_a, interface_b):
        ret = api.dcim.cables.create(
            termination_a_id=interface_a.id,
            termination_a_type="dcim.interface",
            termination_b_id=interface_b.id,
            termination_b_type="dcim.interface",
        )
        yield ret
        ret.delete()

    @pytest.fixture(scope="class")
    def init(self, request, interface_cable):
        self._init_helper(
            request,
            interface_cable,
            filter_kwargs={"id": interface_cable.id},
            endpoint="cables",
            str_repr="Ethernet1 <> Ethernet1",
        )

    def test_trace(self, interface_a):
        test = interface_a.trace()
        assert test
        assert test[0][0].name == "Ethernet1"
        assert test[0][2].name == "Ethernet1"

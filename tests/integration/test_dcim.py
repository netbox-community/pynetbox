import pytest


class TestSimpleServerRackingAndConnecting:

    """Verify we can create, rack, and connect a server."""

    @pytest.fixture
    def site(self, netbox_service, faker):
        """Verify we can create a site."""
        site_name = faker.city()
        site = netbox_service["api"].dcim.sites.create(
            name=site_name, slug=site_name.lower().replace(" ", "_")
        )
        assert site

        return site

    @pytest.fixture
    def rack(self, site, faker):
        """Verify we can create a rack device."""
        rack = site.api.dcim.racks.create(name="rack1", site=site.id)
        assert rack

        return rack

    @pytest.fixture
    def data_leafs(self, rack, faker):
        """Verify we can create data leaf switch devices."""
        devices = []
        for i in [1, 2]:
            device = rack.api.dcim.devices.create(
                name="access_switch%s." % i + faker.domain_name(),
                device_type={"slug": "dcs-7050tx3-48c8"},
                device_role={"name": "Leaf Switch"},
                site=rack.site.id,
                rack=rack.id,
                face="rear",
                position=rack.u_height - i,
            )
            assert device
            devices.append(device)

        return devices

    @pytest.fixture
    def mgmt_leaf(self, rack, faker):
        """Verify we can create data leaf switch devices."""
        device = rack.api.dcim.devices.create(
            name="mgmt_switch1." + faker.domain_name(),
            device_type={"slug": "dcs-7010t-48"},
            device_role={"name": "Leaf Switch"},
            site=rack.site.id,
            rack=rack.id,
            face="rear",
            position=rack.u_height - 3,
        )
        assert device

        return device

    @pytest.fixture
    def server(self, site, faker):
        """Verify we can create a server device."""
        device = site.api.dcim.devices.create(
            name=faker.hostname(),
            device_type={"slug": "dell_poweredge_r640"},
            device_role={"name": "Server"},
            site=site.id,
        )
        assert device

        return device

    def test_racking_server(self, server, data_leafs, mgmt_leaf, rack):
        """Verify we can rack the server."""
        assert server.update(
            {"rack": rack.id, "face": "front", "position": rack.u_height - 4}
        )

        # connect the mgmt iface
        server_mgmt_iface = server.api.dcim.interfaces.get(
            device_id=server.id, mgmt_only=True, cabled=False
        )
        assert server_mgmt_iface

        mleaf_iface = mgmt_leaf.api.dcim.interfaces.filter(
            mgmt_only=False, cabled=False
        )[0]
        cable = server.api.dcim.cables.create(
            termination_a_type="dcim.interface",
            termination_a_id=server_mgmt_iface.id,
            termination_b_type="dcim.interface",
            termination_b_id=mleaf_iface.id,
        )

        # connect the data ifaces in a bond
        server_data_ifaces = server.api.dcim.interfaces.filter(
            device_id=server.id, mgmt_only=False
        )[:2]
        assert len(server_data_ifaces) == 2

        bond_iface = server.api.dcim.interfaces.create(
            device=server.id, name="bond0", type="lag"
        )
        assert bond_iface

        for server_data_iface, data_leaf in zip(server_data_ifaces, data_leafs):
            dleaf_iface = data_leaf.api.dcim.interfaces.filter(
                device_id=data_leaf.id, mgmt_only=False, cabled=False
            )[0]
            cable = server.api.dcim.cables.create(
                termination_a_type="dcim.interface",
                termination_a_id=server_data_iface.id,
                termination_b_type="dcim.interface",
                termination_b_id=dleaf_iface.id,
            )
            assert cable

            assert server_data_iface.update({"lag": bond_iface.id})

        # now reload the server and verify it's set correctly
        server = server.api.dcim.devices.get(server.id)

        # check the cable traces
        for iface in server.api.dcim.interfaces.filter(
            device_id=server.id, cabled=True
        ):
            trace = iface.trace()
            assert len(trace) == 1
            local_iface, cable, remote_iface = trace[0]

            assert local_iface.device.id == server.id
            assert remote_iface.device.id in [dleaf_iface.id] + [
                data_leaf.id for data_leaf in data_leafs
            ]

        # check that it's racked properly
        assert server.rack.id == rack.id

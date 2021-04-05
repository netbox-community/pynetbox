from urllib import parse

import pytest
from packaging import version


DEFAULT_NETBOX_VERSIONS = "2.7, 2.8, 2.9, 2.10"


def pytest_addoption(parser):
    """Hook on the pytest option parser setup.

    Add some extra options to the parser.
    """
    parser.addoption(
        "--netbox-versions",
        action="store",
        default=DEFAULT_NETBOX_VERSIONS,
        help=(
            "The versions of netbox to run integration tests against, as a"
            " comma-separated list. Default: %s" % DEFAULT_NETBOX_VERSIONS
        ),
    )

    parser.addoption(
        "--no-cleanup",
        dest="cleanup",
        action="store_false",
        help=(
            "Skip any cleanup steps after the pytest session finishes. Any containers"
            " created will be left running and the docker-compose files used to"
            " create them will be left on disk."
        ),
    )

    parser.addoption(
        "--url-override",
        dest="url_override",
        action="store",
        help=(
            "Overrides the URL to run tests to. This allows for testing to the same"
            " containers for seperate runs."
        ),
    )


def pytest_configure(config):
    """Hook that runs after test collection is completed.

    Here we can modify items in the collected tests or parser args.
    """
    # verify the netbox versions parse correctly and split them
    config.option.netbox_versions = [
        version.Version(version_string)
        for version_string in config.option.netbox_versions.split(",")
    ]
    if "no:docker" in config.option.plugins and config.option.url_override:

        url_parse = parse.urlparse(config.option.url_override)

        class DockerServicesMock(object):
            def __init__(self, ports):
                self.ports = ports

            def wait_until_responsive(self, *args, **kwargs):
                return None

            def port_for(self, *args):
                return self.ports

        class Plugin:
            @pytest.fixture(scope="session")
            def docker_ip(self):
                return "127.0.0.1"

            @pytest.fixture(scope="session")
            def docker_services(self):
                return DockerServicesMock(url_parse.port)

        config.pluginmanager.register(Plugin())

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

def pytest_configure(config):
    """Hook that runs after test collection is completed.

    Here we can modify items in the collected tests or parser args.
    """
    # verify the netbox versions parse correctly and split them
    config.option.netbox_versions = [
        version.Version(version_string)
        for version_string in config.option.netbox_versions.split(",")
    ]

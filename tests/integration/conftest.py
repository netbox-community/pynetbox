import os
import pytest

import subprocess as subp
import yaml
from packaging import version
import time

import pynetbox
import requests
import atexit


DOCKER_PROJECT_PREFIX = "pytest_pynetbox"


@pytest.fixture(scope="session")
def git_toplevel():
    """Get the top level of the current git repo."""
    return (
        subp.check_output(["git", "rev-parse", "--show-toplevel"])
        .decode("utf-8")
        .splitlines()[0]
    )


@pytest.fixture(scope="session")
def netbox_docker_repo_dirpath(git_toplevel):
    """Get the path to the netbox-docker repo we will use."""
    repo_fpath = os.path.join(git_toplevel, ".netbox-docker")
    if os.path.isdir(repo_fpath):
        subp.check_call(
            [
                "git",
                "fetch",
            ],
            cwd=repo_fpath,
        )
        subp.check_call(
            [
                "git",
                "pull",
            ],
            cwd=repo_fpath,
        )
    else:
        subp.check_call(
            [
                "git",
                "clone",
                "https://github.com/netbox-community/netbox-docker",
                repo_fpath,
            ]
        )

    return repo_fpath


@pytest.fixture(scope="session")
def docker_compose_project_name(pytestconfig):
    """Get the project name to use for docker containers.

    This will return a consistently generated project name so we can kill stale
    containers after the test run is finished.
    """
    return "%s_%s" % (DOCKER_PROJECT_PREFIX, int(time.time()))


def clean_netbox_docker_tmpfiles():
    """Clean up any temporary files created in the netbox-docker repo."""
    dirpath, dirnames, filenames = next(os.walk("./"))
    for filename in filenames:
        if filename.startswith("docker-compose-v"):
            os.remove(filename)


def clean_docker_objects():
    # clean up any containers
    for line in subp.check_output(["docker", "ps"]).decode("utf-8").splitlines():
        words = line.split()
        if not words:
            continue
        if words[-1].startswith(DOCKER_PROJECT_PREFIX):
            print("removing")
            subp.check_call(["docker", "rm", "-f", words[0]])

    # TODO: clean up networks and volumes as well


@pytest.fixture(scope="session")
def docker_compose_file(pytestconfig, netbox_docker_repo_dirpath):
    """Return paths to the compose files needed to create test containers.

    We can create container sets for multiple versions of netbox here by returning a
    list of paths to multiple compose files.
    """
    clean_netbox_docker_tmpfiles()
    clean_docker_objects()

    compose_files = []
    compose_source_fpath = os.path.join(
        netbox_docker_repo_dirpath, "docker-compose.yml"
    )

    for netbox_version in pytestconfig.option.netbox_versions:
        docker_netbox_version = str(netbox_version).replace(".", "_")
        # load the compose file yaml
        compose_data = yaml.safe_load(open(compose_source_fpath, "r").read())

        # add the custom network for this version
        docker_network_name = "%s_v%s" % (DOCKER_PROJECT_PREFIX, docker_netbox_version)
        compose_data["networks"] = {
            docker_network_name: {
                "name": docker_network_name,
            }
        }

        # prepend the netbox version to each of the service names and anything else
        # needed to make the continers unique to the netbox version
        new_services = {}
        for service_name in compose_data["services"].keys():
            new_service_name = "netbox_v%s_%s" % (
                docker_netbox_version,
                service_name,
            )
            new_services[new_service_name] = compose_data["services"][service_name]

            if service_name in ["netbox", "netbox-worker"]:
                # set the netbox image version
                new_services[new_service_name]["image"] = (
                    "netboxcommunity/netbox:v%s" % netbox_version
                )

            # set the network and an alias to the proper short name of the container
            # within that network
            new_services[new_service_name]["networks"] = {
                docker_network_name: {"aliases": [service_name]}
            }

            # fix the naming of any dependencies
            if "depends_on" in new_services[new_service_name]:
                new_service_dependencies = []
                for dependent_service_name in new_services[new_service_name][
                    "depends_on"
                ]:
                    new_service_dependencies.append(
                        "netbox_v%s_%s"
                        % (
                            docker_netbox_version,
                            dependent_service_name,
                        )
                    )
                new_services[new_service_name]["depends_on"] = new_service_dependencies

            # make any internal named volumes unique to the netbox version
            if "volumes" in new_services[new_service_name]:
                new_volumes = []
                for volume_config in new_services[new_service_name]["volumes"]:
                    source = volume_config.split(":")[0]
                    if "/" in source:
                        new_volumes.append(volume_config)
                    else:
                        new_volumes.append(
                            "%s_v%s_%s"
                            % (
                                DOCKER_PROJECT_PREFIX,
                                docker_netbox_version,
                                volume_config,
                            )
                        )
                new_services[new_service_name]["volumes"] = new_volumes

        # replace the services config with the renamed versions
        compose_data["services"] = new_services

        # prepend local volume names
        new_volumes = {}
        for volume_name, volume_config in compose_data["volumes"].items():
            new_volumes[
                "%s_v%s_%s"
                % (
                    DOCKER_PROJECT_PREFIX,
                    docker_netbox_version,
                    volume_name,
                )
            ] = volume_config
        compose_data["volumes"] = new_volumes

        compose_output_fpath = os.path.join(
            netbox_docker_repo_dirpath,
            "docker-compose-v%s.yml" % netbox_version,
        )
        with open(compose_output_fpath, "w") as fdesc:
            fdesc.write(yaml.dump(compose_data))

        compose_files.append(compose_output_fpath)

    yield compose_files

    if pytestconfig.option.cleanup:
        atexit.register(clean_docker_objects)
        atexit.register(clean_netbox_docker_tmpfiles)


def netbox_is_responsive(url):
    """Chack if the HTTP service is up and responsive."""
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return True
    except ConnectionError:
        return False


def id_netbox_service(fixture_value):
    """Create and ID representation for a netbox service fixture param.

    Returns:
        str: Identifiable representation of the service, as best we can

    """
    return "netbox %s" % fixture_value


@pytest.fixture(scope="session")
def netbox_service(pytestconfig, docker_ip, docker_services, request):
    """Ensure that HTTP service is up and responsive."""
    netbox_integration_version = request.param

    # `port_for` takes a container port and returns the corresponding host port
    port = docker_services.port_for(
        "netbox_v%s_nginx" % str(netbox_integration_version).replace(".", "_"), 8080
    )
    url = "http://{}:{}".format(docker_ip, port)
    docker_services.wait_until_responsive(
        timeout=300.0, pause=1, check=lambda: netbox_is_responsive(url)
    )
    return {
        "url": url,
        "netbox_version": netbox_integration_version,
        "api": pynetbox.api(url, token="0123456789abcdef0123456789abcdef01234567"),
    }


def pytest_generate_tests(metafunc):
    """Dynamically parametrize some functions based on args from the cli parser."""
    if "netbox_service" in metafunc.fixturenames:
        # parametrize the requested versions of netbox to the netbox_services fixture
        # so that it will return a fixture for each of the versions requested
        # individually rather than one fixture with multiple versions within it
        metafunc.parametrize(
            "netbox_service",
            metafunc.config.getoption("netbox_versions"),
            ids=id_netbox_service,
            indirect=True,
        )


@pytest.fixture(scope="session")
def docker_cleanup(pytestconfig):
    """Override the docker cleanup command for the containsers used in testing."""
    # pytest-docker does not always clean up after itself properly, and sometimes it
    # will fail during cleanup because there is still a connection to one of the
    # running containers. Here we will disable the builtin cleanup of containers via the
    # pytest-docker module and implement our own instead.

    # There is not a great way to skip the shutdown step, so in this case to skip
    # it we will just pass the "version" arg so the containers are left alone
    command_args = "version"

    return command_args

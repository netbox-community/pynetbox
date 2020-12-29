import os
import pytest

import subprocess as subp
import yaml
from packaging import version
import time

import pynetbox


def netbox_integration_versions():
    versions = []
    for tag in ["v2.9.11", "v2.10.2"]:
        versions.append(
            {
                "tag": tag,
                "docker_tag": tag.replace(".", "_"),
                "version": version.Version(tag),
            }
        )

    return versions


@pytest.fixture(scope="session")
def git_toplevel():
    return (
        subp.check_output(["git", "rev-parse", "--show-toplevel"])
        .decode("utf-8")
        .splitlines()[0]
    )


@pytest.fixture(scope="session")
def netbox_docker_repo_fpath(git_toplevel):
    repo_fpath = "/".join([git_toplevel, ".netbox-docker"])
    if os.path.isdir(repo_fpath):
        subp.check_call(
            ["git", "fetch",], cwd=repo_fpath,
        )
        subp.check_call(
            ["git", "pull",], cwd=repo_fpath,
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
    """Return a consistent project name so we can kill stale containers."""
    return "pytest_pynetbox_%s" % int(time.time())


@pytest.fixture(scope="session")
def docker_compose_file(pytestconfig, netbox_docker_repo_fpath):
    """Return paths to the compose files needed to create test containers.
    
    We can create container sets for multiple versions of netbox here by returning a
    list of paths to multiple compose files.
    """
    compose_files = []
    compose_source_fpath = os.path.join(netbox_docker_repo_fpath, "docker-compose.yml")

    for netbox_integration_version in netbox_integration_versions():
        # load the compose file yaml
        compose_data = yaml.load(open(compose_source_fpath, "r").read())

        # add the custom network for this version
        compose_data["networks"] = {
            "pytest_pynetbox_"
            + netbox_integration_version["docker_tag"]: {
                "name": "pytest_pynetbox_" + netbox_integration_version["docker_tag"],
            }
        }

        # keep track of what each container's name was originally so we can add named
        # links back to them from the other containers within their network
        original_service_names = {}

        # prepend the netbox version to each of the service names and anything else
        # needed to make the continers unique to the netbox version
        new_services = {}
        for service_name in compose_data["services"].keys():
            new_service_name = "netbox_%s_%s" % (
                netbox_integration_version["docker_tag"],
                service_name,
            )
            new_services[new_service_name] = compose_data["services"][service_name]
            original_service_names[new_service_name] = service_name

            if service_name in ["netbox", "netbox-worker"]:
                # set the netbox image version
                new_services[new_service_name]["image"] = (
                    "netboxcommunity/netbox:%s" % netbox_integration_version["tag"]
                )

            # set the network and an alias to the proper short name of the container
            # within that network
            new_services[new_service_name]["networks"] = {
                "pytest_pynetbox_"
                + netbox_integration_version["docker_tag"]: {"aliases": [service_name]}
            }

            # fix the naming of any dependencies
            if "depends_on" in new_services[new_service_name]:
                new_service_dependencies = []
                for dependent_service_name in new_services[new_service_name][
                    "depends_on"
                ]:
                    new_service_dependencies.append(
                        "netbox_%s_%s"
                        % (
                            netbox_integration_version["docker_tag"],
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
                            "pytest_pynetbox_"
                            + netbox_integration_version["docker_tag"]
                            + "_"
                            + volume_config
                        )
                new_services[new_service_name]["volumes"] = new_volumes

        # replace the servives config with the renamed versions
        compose_data["services"] = new_services

        # prepend local volume names
        new_volumes = {}
        for volume_name, volume_config in compose_data["volumes"].items():
            new_volumes[
                "pytest_pynetbox_"
                + netbox_integration_version["docker_tag"]
                + "_"
                + volume_name
            ] = volume_config
        compose_data["volumes"] = new_volumes

        compose_output_fpath = os.path.join(
            git_toplevel,
            ".netbox-docker",
            "docker-compose_%s.yml" % netbox_integration_version["tag"],
        )
        with open(compose_output_fpath, "w") as fdesc:
            fdesc.write(yaml.dump(compose_data))

        compose_files.append(compose_output_fpath)

    return compose_files


def is_responsive(url):
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
    return "netbox %s" % fixture_value["tag"]


@pytest.fixture(
    scope="session", params=netbox_integration_versions(), ids=id_netbox_service
)
def netbox_service(docker_ip, docker_services, request):
    """Ensure that HTTP service is up and responsive."""
    netbox_integration_version = request.param

    # `port_for` takes a container port and returns the corresponding host port
    port = docker_services.port_for(
        "netbox_%s_nginx" % netbox_integration_version["docker_tag"], 8080
    )
    url = "http://{}:{}".format(docker_ip, port)
    docker_services.wait_until_responsive(
        timeout=300.0, pause=1, check=lambda: is_responsive(url)
    )
    return {
        "url": url,
        "netbox_version": netbox_integration_version,
        "api": pynetbox.api(url, token="0123456789abcdef0123456789abcdef01234567"),
    }

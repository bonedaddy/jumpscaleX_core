import subprocess
from loguru import logger

BRANCH = ""


def info(message):
    logger.info(message)


def os_command(command):
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output, error = process.communicate()
    return output, error


def rand_str(size=10):
    return str(uuid.uuid4()).replace("-", "")[:size]


def create_container(container_name, secret):
    info("Create a container")
    command = "/root/.local/bin/3sdk container install name={} explorer=none secret={}".format(container_name, secret)
    os_command(command)

    info("Check that container has been created correctly")
    command = "docker ps -a -f status=running  | grep {}".format(CONTAINER_NAME)
    output, error = os_command(command)
    if CONTAINER_NAME in output.decode():
        return True
    else:
        return False


def docker_install():
    info("Docker install in ubuntu 18.04+")

    info("Update the apt package index and install packages to allow apt to use a repository over HTTPS")
    os_command("sudo apt-get update && sudo apt-get install  -y apt-transport-https ca-certificates curl gnupg-agent \
    software-properties-common")

    info("Add Docker’s official GPG key")
    os_command("curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -")

    info("Set up the stable repository")
    os_command("sudo add-apt-repository \
   \"deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable\"")

    info("Update the apt package index, and install the latest version of Docker Engine and containerd")
    os_command("sudo apt-get update && sudo apt-get -y install docker-ce docker-ce-cli containerd.io")


def install_3sdk():
    info("Install pip3")
    os_command("sudo apt install  -y python3-pip")

    info("Clone jumpscale_core repo")
    CLONE_DIR = "/sandbox/code/github/threefoldtech/jumpscaleX_core"
    os_command("git clone -b {} https://github.com/threefoldtech/jumpscaleX_core/ {}".format(BRANCH, CLONE_DIR))

    info("Install 3sdk")
    os_command("cd {}/install && pip3 install --user -e .".format(CLONE_DIR))


def before_all():
    info("docker Install")
    docker_install()

    info("Check that docker is installed correctly")
    output, error = os_command("docker --version")
    assert "Docker version" in output.decode(), "Command 'docker' not found"

    info("Install 3sdk")
    install_3sdk()

    info("Check that 3sdk is installed correctly")
    output, error = os_command("/root/.local/bin/3sdk --help")
    assert "usage: 3sdk" in output.decode(), "3sdk doesn't installed yet"


def after_all():
    info("Clean the installation")
    command = "rm -rf /sandbox/"
    os_command(command)


def test01_container_delete_with_and_without_name_argument():
    """
    Test container delete

    #. Create a container.
    #. Check that the container has been created correctly.
    #. Use delete argument with name option to delete the created container.
    #. Check that the container is has been deleted.
    #. Create two containers.
    #. Use delete argument without name option to delete the last two containers.
    #. Check that the two containers has been delete

    """

    info("Create three containers")
    info("Check that container has been created correctly")

    container_1 = rand_str()
    secret_1 = rand_str()
    assert create_container(container_1, secret_1), "{} doesn't created correctly".format(container_1)

    info("Use delete argument with name option to delete the created container")
    command = "/root/.local/bin/3sdk delete name={}".format(container_1)
    os_command(command)

    info("Check that container has been deleted correctly")
    command = "docker ps -a -f status=running  | grep {}".format(container_1)
    output, error = os_command(command)
    assert container_name_1 not in output.decode()

    info("Create 2 containers")
    container_2 = rand_str()
    container_3 = rand_str()
    assert create_container(container_2, container_2), "{} doesn't created correctly".format(container_2)
    assert create_container(container_3, container_3), "{} doesn't created correctly".format(container_3)

    info("Check that container has been deleted correctly")
    for container in container_2, container_3:

        command = "docker ps -a -f status=running  | grep {}".format(container)
        output, error = os_command(command)
        assert container not in output.decode()


import argparse
import os
import re
import shlex
import subprocess
from pathlib import Path

from fabric import ThreadingGroup


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--number', type=int, required=True, help='Docker Swarm Cluster Size')
    parser.add_argument('-a', '--ip', type=str, required=True, help='Manager IP')
    parser.add_argument('-cn', '--client-number', type=int, required=True, help='Client Cluster Size')
    return parser.parse_args()


install_docker = '''if ! command -v docker &> /dev/null; then
    echo "Docker not found, proceeding with installation"
    sudo apt-get update && \
    sudo DEBIAN_FRONTEND=noninteractive apt-get -y install \
    ca-certificates curl gnupg lsb-release && \
    sudo install -m 0755 -d /etc/apt/keyrings && \
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --batch --yes --dearmor -o /etc/apt/keyrings/docker.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | \
    sudo tee /etc/apt/sources.list.d/docker.list > /dev/null && \
    sudo apt-get update && \
    sudo DEBIAN_FRONTEND=noninteractive apt-get install -y docker-ce docker-ce-cli containerd.io && \
    echo "Docker installed successfully"

    # Stop Docker service before making changes
    sudo systemctl stop docker

    # Create new directory for Docker data
    sudo rm -rf /docker-store/data/*
    sudo mkdir -p /docker-store/data/docker

    # Configure Docker to use the new directory for data storage
    echo '{"data-root": "/docker-store/data/docker"}' | sudo tee /etc/docker/daemon.json > /dev/null

    # Optionally, move existing Docker data from /var/lib/docker to /docker-store/data/docker
    if [ -d "/var/lib/docker" ]; then
        echo "Moving existing Docker data from /var/lib/docker to /docker-store/data/docker"
        sudo rsync -aP /var/lib/docker/ /docker-store/data/docker/
    fi

    # Restart Docker service
    sudo systemctl start docker
else
    echo "Docker is already installed, skipping installation"
fi
'''

leave_swarm_forcefully = '''if docker info | grep -q "Swarm: active"; then
    echo "Node is part of a swarm, leaving the swarm forcefully"
    sudo docker swarm leave --force
else
    echo "Node is not part of a swarm, skipping swarm leave"
fi
'''

install_collectl = 'sudo apt-get update && sudo DEBIAN_FRONTEND=noninteractive apt-get install -y collectl'
install_sysdig = 'sudo apt-get update && sudo DEBIAN_FRONTEND=noninteractive apt-get install -y sysdig'
delete_repo = 'rm -rf DeathStarBench'
clone_official_socialnetwork_repo = 'ssh-keygen -F github.com || ssh-keyscan github.com >> ~/.ssh/known_hosts && git clone https://github.com/delimitrou/DeathStarBench.git && cd DeathStarBench && git checkout b2b7af9 && cd ..'
args = parse_args()

with ThreadingGroup(*[f'node-{idx}' for idx in range(0, args.number)]) as swarm_grp, \
        ThreadingGroup(*[f'node-{idx}' for idx in range(args.number, args.number + args.client_number)]) as client_grp:
    swarm_grp.run(delete_repo)


    def stop_swarm_cluster():
        swarm_grp.run('sudo docker swarm leave')
        subprocess.run(shlex.split('sudo docker swarm leave -f'))


    def clear_env():
        swarm_grp.run(
            'sudo apt-get -y purge docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin docker-ce-rootless-extras')
        swarm_grp.run(
            'for pkg in docker.io docker-doc docker-compose docker-compose-v2 podman-docker containerd runc; do sudo apt-get remove $pkg; done')
        swarm_grp.run('sudo rm -rf /var/lib/containerd')
        swarm_grp.run('sudo rm -rf /var/lib/docker')
        swarm_grp.run('sudo rm /etc/apt/keyrings/docker.gpg')


    swarm_grp.run(install_collectl)
    print('** collectl installed **')
    swarm_grp.run(clone_official_socialnetwork_repo)
    print('** socialNetwork cloned **')

    swarm_grp.run(install_docker)
    print('** docker installed **')

    # Initialize Docker Swarm
    ret = subprocess.run(['sudo', 'docker', 'swarm', 'init', '--advertise-addr', args.ip], capture_output=True)
    print('** swarm manager initialized **')
    swarm_join_cmd_ptn = r'(docker swarm join --token .*:\d+)'
    swarm_join_cmd = re.search(swarm_join_cmd_ptn, ret.stdout.decode('utf-8'))
    if swarm_join_cmd is None:
        print('Didn\'t find match pattern for docker swarm join:')
        print(f'The ret of swarm init is {ret}')
        exit(0)
    else:
        swarm_join_cmd = swarm_join_cmd.group()
    with ThreadingGroup.from_connections(swarm_grp[1:]) as grp_worker:
        grp_worker.run('sudo ' + swarm_join_cmd)
        grp_worker.run(
            'if [ ! -e "$HOME/.ssh/config" ]; then echo -e "Host *\n\tStrictHostKeyChecking no" >> $HOME/.ssh/config; fi')
        grp_worker.put(Path.home() / '.ssh' / 'id_rsa', '.ssh')
    print('** swarm cluster ready **')

    subprocess.run(shlex.split('sudo docker service create --name registry \
                               --publish published=5000,target=5000 registry:2'))
    print('** registry service created **')

    client_grp[0].run(install_sysdig)
    client_grp.put(Path.home() / '.ssh/id_rsa', '.ssh')
    client_grp.run(
        'if [ ! -e "$HOME/.ssh/config" ]; then echo -e "Host *\n\tStrictHostKeyChecking no" >> $HOME/.ssh/config; fi')
    client_grp.put(Path.home() / 'RubbosClient.zip')
    client_grp.run('unzip RubbosClient.zip')
    client_grp.run('mv RubbosClient/elba .')
    client_grp.run('mv RubbosClient/rubbos .')
    client_grp.run('gcc $HOME/elba/rubbos/RUBBoS/bench/flush_cache.c -o $HOME/elba/rubbos/RUBBoS/bench/flush_cache')
    print('** RubbosClient copied **')

    os.chdir(Path.home())
    for file in ['src', 'RubbosClient_src', 'socialNetwork', 'scripts_limit', 'internal_triggers']:
        subprocess.run(shlex.split(f'unzip {file}.zip'))
    subprocess.run(shlex.split('mv DeathStarBench/socialNetwork/src DeathStarBench/socialNetwork/src.bk'))
    subprocess.run(shlex.split('mv src DeathStarBench/socialNetwork/'))
    os.chdir(Path.home() / 'DeathStarBench' / 'socialNetwork')
    subprocess.run(shlex.split('sudo docker build -t 127.0.0.1:5000/social-network-microservices:withLog_01 .'))
    subprocess.run(shlex.split('sudo docker push 127.0.0.1:5000/social-network-microservices:withLog_01'))
    os.chdir(Path.home() / 'internal_triggers' / 'cpu')
    subprocess.run(shlex.split('sudo docker build -t 127.0.0.1:5000/cpu_intensive .'))
    subprocess.run(shlex.split('sudo docker push 127.0.0.1:5000/cpu_intensive'))
    os.chdir(Path.home() / 'internal_triggers' / 'io')
    subprocess.run(shlex.split('sudo docker build -t 127.0.0.1:5000/io_intensive .'))
    subprocess.run(shlex.split('sudo docker push 127.0.0.1:5000/io_intensive'))
    print('** customized socialNetwork docker images built **')

    os.chdir(Path.home())
    subprocess.run('rsync -a --remove-source-files socialNetwork/ DeathStarBench/socialNetwork/', shell=True)
    subprocess.run(shlex.split('rm -r socialNetwork/scripts'))
    os.chdir(Path.home() / 'DeathStarBench' / 'socialNetwork')
    subprocess.run(shlex.split('sudo chmod +x ./start.sh'))
    subprocess.run(shlex.split('sudo ./start.sh start'))
    print('** socialNetwork stack deployed **')

    subprocess.run(shlex.split(f"chmod -R +x {Path.home()}/DeathStarBench/"))
    os.chdir(Path.home() / 'RubbosClient_src')
    subprocess.run(shlex.split('mvn clean'))
    subprocess.run(shlex.split('mvn package'))
    subprocess.run(shlex.split('chmod +x ./cpToCloud.sh'))
    subprocess.run(shlex.split('./cpToCloud.sh'))
    print('** client binary distributed **')

    # we move register here to ensure all the services have launched
    os.chdir(Path.home() / 'DeathStarBench' / 'wrk2')
    subprocess.run('make')
    subprocess.run(shlex.split('sudo apt-get -y install libssl-dev libz-dev luarocks'))
    subprocess.run(shlex.split('sudo luarocks install luasocket'))
    os.chdir(Path.home() / 'DeathStarBench' / 'socialNetwork')
    # TODO: check if socialNetwork is successfully deployed
    subprocess.run(shlex.split('sudo ./start.sh register'))
    subprocess.run(shlex.split('sudo ./start.sh compose'))
    print('** socialNetwork data created **')

    subprocess.run(shlex.split('./start.sh dedicate'))
    print('** core dedicated **\n** all the work is done, begin running the experiment **')

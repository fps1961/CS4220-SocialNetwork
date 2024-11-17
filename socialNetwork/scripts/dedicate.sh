
#!/bin/bash


ssh node-0 'containerid=$(sudo docker ps -aqf "name=^socialNetwork_user-mongodb"); sudo docker update --cpuset-cpus "1-4" $containerid'
ssh node-0 'containerid=$(sudo docker ps -aqf "name=^socialNetwork_home-timeline-service"); sudo docker update --cpuset-cpus "6" $containerid'

ssh node-1 'containerid=$(sudo docker ps -aqf "name=^socialNetwork_post-storage-mongodb"); sudo docker update --cpuset-cpus 2 $containerid'
ssh node-1 'containerid=$(sudo docker ps -aqf "name=^socialNetwork_post-storage-service"); sudo docker update --cpuset-cpus "6" $containerid'
ssh node-1 'containerid=$(sudo docker ps -aqf "name=^socialNetwork_media-memcached"); sudo docker update --cpuset-cpus 7 $containerid'

ssh node-2 'containerid=$(sudo docker ps -aqf "name=^socialNetwork_post-storage-memcached"); sudo docker update --cpuset-cpus 1 $containerid'
ssh node-2 'containerid=$(sudo docker ps -aqf "name=^socialNetwork_media-service"); sudo docker update --cpuset-cpus 2 $containerid'
ssh node-2 'containerid=$(sudo docker ps -aqf "name=^socialNetwork_compose-post-service"); sudo docker update --cpuset-cpus 3 $containerid'
ssh node-2 'containerid=$(sudo docker ps -aqf "name=^socialNetwork_home-timeline-redis"); sudo docker update --cpuset-cpus 4 $containerid'
ssh node-2 'containerid=$(sudo docker ps -aqf "name=^socialNetwork_user-mention-service"); sudo docker update --cpuset-cpus 5 $containerid'
ssh node-2 'containerid=$(sudo docker ps -aqf "name=^socialNetwork_social-graph-mongodb"); sudo docker update --cpuset-cpus 6 $containerid'
ssh node-2 'containerid=$(sudo docker ps -aqf "name=^socialNetwork_url-shorten-service"); sudo docker update --cpuset-cpus 7 $containerid'

ssh node-3 'containerid=$(sudo docker ps -aqf "name=^socialNetwork_text-service"); sudo docker update --cpuset-cpus 2 $containerid'
ssh node-3 'containerid=$(sudo docker ps -aqf "name=^socialNetwork_url-shorten-memcached"); sudo docker update --cpuset-cpus 3 $containerid'
ssh node-3 'containerid=$(sudo docker ps -aqf "name=^socialNetwork_media-mongodb"); sudo docker update --cpuset-cpus 4 $containerid'
ssh node-3 'containerid=$(sudo docker ps -aqf "name=^socialNetwork_social-graph-service"); sudo docker update --cpuset-cpus 5 $containerid'
ssh node-3 'containerid=$(sudo docker ps -aqf "name=^socialNetwork_media-frontend"); sudo docker update --cpuset-cpus 6 $containerid'
ssh node-3 'containerid=$(sudo docker ps -aqf "name=^socialNetwork_user-timeline-redis"); sudo docker update --cpuset-cpus 7 $containerid'
ssh node-3 'containerid=$(sudo docker ps -aqf "name=^socialNetwork_cpu-intensive"); sudo docker update --cpuset-cpus 7 $containerid'
ssh node-3 'containerid=$(sudo docker ps -aqf "name=^socialNetwork_io-intensive"); sudo docker update --cpuset-cpus 7 $containerid'

ssh node-4 'containerid=$(sudo docker ps -aqf "name=^socialNetwork_user-memcached"); sudo docker update --cpuset-cpus 2 $containerid'
ssh node-4 'containerid=$(sudo docker ps -aqf "name=^socialNetwork_social-graph-redis"); sudo docker update --cpuset-cpus 3 $containerid'
ssh node-4 'containerid=$(sudo docker ps -aqf "name=^socialNetwork_user-service"); sudo docker update --cpuset-cpus 4 $containerid'
ssh node-4 'containerid=$(sudo docker ps -aqf "name=^socialNetwork_user-timeline-mongodb"); sudo docker update --cpuset-cpus 5 $containerid'
ssh node-4 'containerid=$(sudo docker ps -aqf "name=^socialNetwork_user-timeline-service"); sudo docker update --cpuset-cpus 6 $containerid'
ssh node-4 'containerid=$(sudo docker ps -aqf "name=^socialNetwork_unique-id-service"); sudo docker update --cpuset-cpus 7 $containerid'

ssh node-5 'containerid=$(sudo docker ps -aqf "name=^socialNetwork_url-shorten-mongodb"); sudo docker update --cpuset-cpus 1 $containerid'
ssh node-5 'containerid=$(sudo docker ps -aqf "name=^socialNetwork_nginx-web-server"); sudo docker update --cpuset-cpus "0-7" $containerid'

## example of how to replay back the collectl results
#collectl -scdn -p ./VMelba9-20130922-083628.raw  -P -f . -oUmz --from 20130922:08:36-08:39

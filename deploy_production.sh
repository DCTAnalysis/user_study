# stop and remove old containers
docker stop nginx
docker rm nginx
docker stop flask_server_prod
docker rm flask_server_prod
docker stop db
docker rm db

# remove old images
docker rmi flask_server_prod:latest
docker rmi nginx:1.19.4-alpine
docker rmi mysql:latest
docker rmi certbot/certbot:latest
docker rmi 3.8-alpine

# start database, nginx, and nodejs containers and init certificate 
docker-compose up -d database
docker-compose up -d flask_server_prod
sudo DOMAIN=$DOMAIN DOMAIN_MAIL=$DOMAIN_MAIL /bin/bash ./init_letsencrypt.sh

# start database
docker-compose up --d database
# start development version of flask server
docker-compose up --build flask_server_dev
# remove development version of flask server instance and image
docker rm flask_server_dev
docker rmi flask_server_dev

# start database_export container
docker-compose up --build database_export 
# remove database_export instance and image
docker rm db_export
docker rmi db_export

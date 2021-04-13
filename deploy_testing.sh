# start test database
docker-compose up --d database_test
# start flask server test instance and run tests
docker-compose up --build flask_server_test
# stop test database and remove it
docker stop db_test
docker rm db_test
# remove flask server test instance and image
docker rm flask_server_test
docker rmi flask_server_test
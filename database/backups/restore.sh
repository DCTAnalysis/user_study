cat backup.sql | docker exec -i db /usr/bin/mysql -u $MYSQL_USER --password="$MYSQL_PASSWORD" domain_user_study

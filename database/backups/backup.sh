docker exec db /usr/bin/mysqldump --no-tablespaces -u $MYSQL_USER --password="$MYSQL_PASSWORD" domain_user_study > backup.sql

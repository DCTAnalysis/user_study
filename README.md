# 2020-malicious-domain-study

Follow-up on AsiaCCS paper on users' perception of malicious domains.

# Setup

This assumes you want to deploy on some machine which runs docker.

### 1. Create .env files

You will have to create a .env and .env.test file, which must contain the following options:

**.env.test**
```
MYSQL_USER=<SOME USER>
MYSQL_PASSWORD=<PASSWORD>
MYSQL_ROOT_PASSWORD=<ROOT_PASSWORD>
MYSQL_DATABASE=domain_user_study
MYSQL_HOST=database_test
CHECK_LAST_UNFINISHED_STEP=0
```

The prod file is similar with the following changes:

```
MYSQL_HOST=database
CHECK_LAST_UNFINISHED_STEP=1
```

### 2. Setup app.conf
Add the domain you want to deploy in:
data/nginx/app.conf

### 3. Add your Information
Add the information on who you are in:

flask_server/src/templates/index.html
flask_server/src/templates/consent.html

### 4. Deploy
Deploy using the deploy_production script.
We automatically create a certificate using letsencrypt.

```
DOMAIN=<domain you want to deploy to> DOMAIN_MAIL=<mail for certificate> ./deploy_production.sh
```

# Backup/Restore database

We offer export scripts to dump the database in database/backups/.
You will have to supply the MYSQL_USER and MYSQL_PASSWORD when you use these.
When you use [dotenv](https://pypi.org/project/python-dotenv/), you can simply run:

```
dotenv run -- ./database/backups/backup.sh
```

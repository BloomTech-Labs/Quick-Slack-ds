### Database setup
The app uses [Flask-Migrate]('https://flask-migrate.readthedocs.io/en/latest/') to manage schema updates

Run `docker-compose run flask flask db upgrade` on an empty db to initialize the database.

#### Importing data from database dump
 - While the app is running with `docker-compose up` find the container ID of the database by running `docker ps`. It should be named something like `$PROJECTDIR_postgres:latest` 
 - Run `cat db_dumpfile.sql| docker exec -t psql -u postgres` to load the database file.

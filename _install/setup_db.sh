#!/usr/bin/env bash

sudo apt install -y postgresql
sudo su - postgres
sudo nano /etc/postgresql/9.5/main/pg_hba.conf
# make the following change
# local   all             all                                     peer
# local   all             all                                     md5
sudo service postgresql restart
psql
# now running in psql shell
CREATE DATABASE gnaf;
\connect gnaf;
CREATE SCHEMA gnaf;
CREATE USER gnafusr WITH PASSWORD 'xxxxxx';
ALTER DATABASE gnaf OWNER TO gnafusr;
GRANT ALL ON DATABASE gnaf TO gnafusr;
GRANT ALL ON SCHEMA gnaf TO gnafusr;

# do this after view creation
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA gnaf TO gnafusr;

# ensure DB number lookups are integers, not VARCHARS
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
CREATE USER gnafusr WITH PASSWORD 'gnafrocks';
ALTER DATABASE gnaf OWNER TO gnafusr;

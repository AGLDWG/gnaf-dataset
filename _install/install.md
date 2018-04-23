# Install
For Ubuntu Linux

# basic server things
`sudo apt update`  
`sudo timedatectl set-timezone Australia/Brisbane`  
`sudo apt install unzip`  
`sudo apt install git`  


## Get the GNAF
`curl https://data.gov.au/dataset/19432f89-dc3a-4ef3-b943-5326ef1dbecc/resource/4b084096-65e4-4c8e-abbe-5e54ff85f42f/download/nov17gnafpipeseparatedvalue20180108083723.zip`
`unzip nov17gnafpipeseparatedvalue20180108083723.zip`  
   
## Install Postgres

`sudo apt install postgresql`  
`sudo apt install -y postgresql-contrib`  

*As postgres user:*  
`createdb gnaf`  
`greateuser gnafusr`  
*\# log in to gnaf DB*  
`psql gnaf`  

*As logged in to Postgres as postgres super user:*  
`CREATE SCHEMA gnaf;`  
`GRANT ALL PRIVILEGES ON DATABASE gnaf TO gnafusr;`    
`ALTER USER gnafusr WITH PASSWORD 'xxxx';`  

\# run the script prepare_scripts.sh using the directory of the GNAF content
\# run the run_sql.sh script
Do this by logging into postgres as the postgres super user from within the gnafldapi _load dir:
`cd /var/www/gnafldapi/_load/`
`su - postgres`  
`psql gnaf`  


## Install LDAPI requirements
### Apache
`sudo apt install -y apache2`  
`sudo apt install libapache2-mod-wsgi-py3`  
`sudo service apache2 restart`  
\# check apache is online at IP address  

### LDAPI repo
`cd /var/www/`  
`sudo mkdir gnafldapi`  
`sudo chown -R ubuntu gnafldapi`  
`cd gnafldapi/`  
`git clone http://github.com/nicholascar/gnaf-ldapi-test.git .`  

### Python3
`sudo apt install -y python3-pip`  
`pip3 install --upgrade pip`  
`pip3 install -r requirements.txt` \# this seems to do nothing  
`sudo apt install -y python3-flask`  
`sudo apt install -y python3-rdflib`


## Updating GNAF content
### Get latest GNAF
`curl https://data.gov.au/dataset/19432f89-dc3a-4ef3-b943-5326ef1dbecc/resource/4b084096-65e4-4c8e-abbe-5e54ff85f42f/download/feb18gnafpipeseparatedvalue20180219141901.zip > feb18.zip`
`unzip feb18.zip`

### Get the latest GNAF code lists' SQL
`curl http://gnafld.net/def/gnaf/code/codes.sql > create_codes.sql`

### Prepare loading scripts, run them
alter the PSV file location in prepare_scripts.sh to match new folder then
`./prepare_scripts.sh`

inside Postgres:
`\i run_sql.sh`

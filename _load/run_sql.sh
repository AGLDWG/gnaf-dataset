#!/usr/bin/env bash

echo "running SQL scripts"
psql -U gnaf -d gnaf -a -f tables_create.sql
echo "tables created"
psql -U gnaf -d gnaf -a -f address_view_create.sql
echo "address view created"
psql -U gnaf -d gnaf -a -f authority_codes_load.sql
echo "authority codes loaded"
psql -U gnaf -d gnaf -a -f standard_tables_load.sql
echo "standard tables loaded"
psql -U gnaf -d gnaf -a -f add_fk_constraints.sql
echo "foreign key constraints added"
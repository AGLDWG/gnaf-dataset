#!/usr/bin/env bash

SCRIPT_DIR=$(dirname "$0")
PSV_FOLDERS_DIR="/Users/car587/work/gnaf-ldapi-test/_install/FEB18_GNAF_PipeSeparatedValue_20180219141901/G-NAF/G-NAF\ FEBRUARY\ 2018/"

sed "s@{PSV_FOLDERS_DIR}@$PSV_FOLDERS_DIR@g" < "$SCRIPT_DIR/authority_codes_load.sql.template" > "$SCRIPT_DIR/authority_codes_load.sql"
# put in the right folder
sed "s@{PSV_FOLDERS_DIR}@$PSV_FOLDERS_DIR@g" < "$SCRIPT_DIR/standard_tables_load.sql.template" > "$SCRIPT_DIR/standard_tables_load.sql"
# do one per STATE
sed "s@{STATE}@ACT@g" < "$SCRIPT_DIR/standard_tables_load.sql" > "$SCRIPT_DIR/standard_tables_load_ACT.sql"
sed "s@{STATE}@NSW@g" < "$SCRIPT_DIR/standard_tables_load.sql" > "$SCRIPT_DIR/standard_tables_load_NSW.sql"
sed "s@{STATE}@NT@g" < "$SCRIPT_DIR/standard_tables_load.sql" > "$SCRIPT_DIR/standard_tables_load_NT.sql"
sed "s@{STATE}@OT@g" < "$SCRIPT_DIR/standard_tables_load.sql" > "$SCRIPT_DIR/standard_tables_load_OT.sql"
sed "s@{STATE}@QLD@g" < "$SCRIPT_DIR/standard_tables_load.sql" > "$SCRIPT_DIR/standard_tables_load_QLD.sql"
sed "s@{STATE}@SA@g" < "$SCRIPT_DIR/standard_tables_load.sql" > "$SCRIPT_DIR/standard_tables_load_SA.sql"
sed "s@{STATE}@TAS@g" < "$SCRIPT_DIR/standard_tables_load.sql" > "$SCRIPT_DIR/standard_tables_load_TAS.sql"
sed "s@{STATE}@VIC@g" < "$SCRIPT_DIR/standard_tables_load.sql" > "$SCRIPT_DIR/standard_tables_load_VIC.sql"
sed "s@{STATE}@WA@g" < "$SCRIPT_DIR/standard_tables_load.sql" > "$SCRIPT_DIR/standard_tables_load_WA.sql"

rm "$SCRIPT_DIR/standard_tables_load.sql"

#!/usr/bin/env bash

SCRIPT_DIR=$(dirname "$0")
PSV_FOLDERS_DIR="/home/ubuntu/AUG17_GNAF_PipeSeparatedValue_20170821153434/G-NAF/G-NAF AUGUST 2017/"

sed "s@{PSV_FOLDERS_DIR}@$PSV_FOLDERS_DIR@g" < "$SCRIPT_DIR/authority_codes_load.sql.template" > "$SCRIPT_DIR/authority_codes_load.sql"
sed "s@{PSV_FOLDERS_DIR}@$PSV_FOLDERS_DIR@g" < "$SCRIPT_DIR/standard_tables_load.sql.template" > "$SCRIPT_DIR/standard_tables_load.sql"
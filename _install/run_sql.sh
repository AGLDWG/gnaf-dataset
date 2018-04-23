# in psql as postgres superuser

\i create_tables.sql
\i authority_codes_load.sql
\i standard_tables_load_ACT.sql
\i standard_tables_load_NSW.sql
\i standard_tables_load_NT.sql
\i standard_tables_load_OT.sql
\i standard_tables_load_QLD.sql
\i standard_tables_load_SA.sql
\i standard_tables_load_TAS.sql
\i standard_tables_load_VIC.sql
\i standard_tables_load_WA.sql
\i create_fk_constraints.sql
\i create_views.sql
\i create_indexes.sql
\i create_codes.sql

GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA gnaf TO gnafusr;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA codes TO gnafusr;
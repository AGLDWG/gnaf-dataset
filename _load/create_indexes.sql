-- DROP INDEX gnaf.ix_addressalias_principal_alias;
CREATE INDEX ix_addressalias_principal_alias
  ON gnaf.address_alias
  USING btree
  (principal_pid, alias_pid);

-- DROP INDEX gnaf.ix_addressalias_alias_principal;
CREATE INDEX ix_addressalias_alias_principal
  ON gnaf.address_alias
  USING btree
  (alias_pid, principal_pid);

-- DROP INDEX gnaf.ix_addressdefaultgeocode_addressdetailpid;
CREATE INDEX ix_addressdefaultgeocode_addressdetailpid
  ON gnaf.address_default_geocode
  USING btree
  (address_detail_pid);

-- DROP INDEX gnaf.ix_addressdetail_address;
CREATE INDEX ix_addressdetail_address
  ON gnaf.address_detail
  USING btree
  (address_detail_pid, street_locality_pid, locality_pid, CAST(CAST(confidence AS integer) AS numeric));

-- DROP INDEX gnaf.ix_addressmeshblock2011_addressdetailpid_mb2011pid;
CREATE INDEX ix_addressmeshblock2011_addressdetailpid_mb2011pid
  ON gnaf.address_mesh_block_2011
  USING btree
  (address_detail_pid, mb_2011_pid);

-- DROP INDEX gnaf.ix_addressmeshblock2016_addressdetailpid_mb2016pid;
CREATE INDEX ix_addressmeshblock2016_addressdetailpid_mb2016pid
  ON gnaf.address_mesh_block_2016
  USING btree
  (address_detail_pid, mb_2016_pid);

-- DROP INDEX gnaf.ix_locality_localitypid_statepid;
CREATE INDEX ix_locality_localitypid_statepid
  ON gnaf.locality
  USING btree
  (locality_pid, state_pid);

-- DROP INDEX gnaf.ix_primarysecondary_primary_secondary;
CREATE INDEX ix_primarysecondary_primary_secondary
  ON gnaf.primary_secondary
  USING btree
  (primary_pid, secondary_pid);

-- DROP INDEX gnaf.ix_primarysecondary_secondary_primary;
CREATE INDEX ix_primarysecondary_secondary_primary
  ON gnaf.primary_secondary
  USING btree
  (secondary_pid, primary_pid);

-- DROP INDEX gnaf.ix_streetlocality_streetlocalitypid_localitypid;
CREATE INDEX ix_streetlocality_streetlocalitypid_localitypid
  ON gnaf.street_locality
  USING btree
  (street_locality_pid, locality_pid);

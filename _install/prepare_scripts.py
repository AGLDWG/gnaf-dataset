import os


# -- Directory of the G-NAF content (please include the trailing slash) ---------------------------------
PSV_FOLDERS_DIR = ''
STATES = ['ACT', 'NSW', 'NT', 'OT', 'QLD', 'SA', 'TAS', 'VIC', 'WA']

if PSV_FOLDERS_DIR == '':
	raise Exception('The PSV_FOLDERS_DIR has not been set.')


def create_authority_codes_sql_file(PSV_FOLDERS_DIR):
	# Authority Codes Load SQL
	authority_codes_template = ''
	authority_codes_template += os.path.join(f"COPY gnaf.address_alias_type_aut FROM '{PSV_FOLDERS_DIR}Authority Code", "Authority_Code_ADDRESS_ALIAS_TYPE_AUT_psv.psv' WITH (format csv, header true, delimiter E'|', NULL '');\n")
	authority_codes_template += os.path.join(f"COPY gnaf.address_type_aut FROM '{PSV_FOLDERS_DIR}Authority Code", "Authority_Code_ADDRESS_TYPE_AUT_psv.psv' WITH (format csv, header true, delimiter E'|', NULL '');\n")
	authority_codes_template += os.path.join(f"COPY gnaf.flat_type_aut FROM '{PSV_FOLDERS_DIR}Authority Code", "Authority_Code_FLAT_TYPE_AUT_psv.psv' WITH (format csv, header true, delimiter E'|', NULL '');\n")
	authority_codes_template += os.path.join(f"COPY gnaf.geocode_reliability_aut FROM '{PSV_FOLDERS_DIR}Authority Code", "Authority_Code_GEOCODE_RELIABILITY_AUT_psv.psv' WITH (format csv, header true, delimiter E'|', NULL '');\n")
	authority_codes_template += os.path.join(f"COPY gnaf.geocode_type_aut FROM '{PSV_FOLDERS_DIR}Authority Code", "Authority_Code_GEOCODE_TYPE_AUT_psv.psv' WITH (format csv, header true, delimiter E'|', NULL '');\n")
	authority_codes_template += os.path.join(f"COPY gnaf.geocoded_level_type_aut FROM '{PSV_FOLDERS_DIR}Authority Code", "Authority_Code_GEOCODED_LEVEL_TYPE_AUT_psv.psv' WITH (format csv, header true, delimiter E'|', NULL '');\n")
	authority_codes_template += os.path.join(f"COPY gnaf.level_type_aut FROM '{PSV_FOLDERS_DIR}Authority Code", "Authority_Code_LEVEL_TYPE_AUT_psv.psv' WITH (format csv, header true, delimiter E'|', NULL '');\n")
	authority_codes_template += os.path.join(f"COPY gnaf.locality_alias_type_aut FROM '{PSV_FOLDERS_DIR}Authority Code", "Authority_Code_LOCALITY_ALIAS_TYPE_AUT_psv.psv' WITH (format csv, header true, delimiter E'|', NULL '');\n")
	authority_codes_template += os.path.join(f"COPY gnaf.locality_class_aut FROM '{PSV_FOLDERS_DIR}Authority Code", "Authority_Code_LOCALITY_CLASS_AUT_psv.psv' WITH (format csv, header true, delimiter E'|', NULL '');\n")
	authority_codes_template += os.path.join(f"COPY gnaf.mb_match_code_aut FROM '{PSV_FOLDERS_DIR}Authority Code", "Authority_Code_MB_MATCH_CODE_AUT_psv.psv' WITH (format csv, header true, delimiter E'|', NULL '');\n")
	authority_codes_template += os.path.join(f"COPY gnaf.ps_join_type_aut FROM '{PSV_FOLDERS_DIR}Authority Code", "Authority_Code_PS_JOIN_TYPE_AUT_psv.psv' WITH (format csv, header true, delimiter E'|', NULL '');\n")
	authority_codes_template += os.path.join(f"COPY gnaf.street_class_aut FROM '{PSV_FOLDERS_DIR}Authority Code", "Authority_Code_STREET_CLASS_AUT_psv.psv' WITH (format csv, header true, delimiter E'|', NULL '');\n")
	authority_codes_template += os.path.join(f"COPY gnaf.street_locality_alias_type_aut FROM '{PSV_FOLDERS_DIR}Authority Code", "Authority_Code_STREET_LOCALITY_ALIAS_TYPE_AUT_psv.psv' WITH (format csv, header true, delimiter E'|', NULL '');\n")
	authority_codes_template += os.path.join(f"COPY gnaf.street_suffix_aut FROM '{PSV_FOLDERS_DIR}Authority Code", "Authority_Code_STREET_SUFFIX_AUT_psv.psv' WITH (format csv, header true, delimiter E'|', NULL '');\n")
	authority_codes_template += os.path.join(f"COPY gnaf.street_type_aut FROM '{PSV_FOLDERS_DIR}Authority Code", "Authority_Code_STREET_TYPE_AUT_psv.psv' WITH (format csv, header true, delimiter E'|', NULL '');")

	with open('authority_codes_load.sql', 'w+') as f:
		f.write(authority_codes_template)


def create_state_sql_files(PSV_FOLDERS_DIR):
	for STATE in STATES:
		template = ""
		template += os.path.join(f"COPY gnaf.address_alias FROM '{PSV_FOLDERS_DIR}Standard", f"{STATE}_ADDRESS_ALIAS_psv.psv' WITH (format csv, header true, delimiter E'|', NULL '');\n")
		template += os.path.join(f"COPY gnaf.address_default_geocode FROM '{PSV_FOLDERS_DIR}Standard", f"{STATE}_ADDRESS_DEFAULT_GEOCODE_psv.psv' WITH (format csv, header true, delimiter E'|', NULL '');\n")
		template += os.path.join(f"COPY gnaf.address_detail FROM '{PSV_FOLDERS_DIR}Standard", f"{STATE}_ADDRESS_DETAIL_psv.psv' WITH (format csv, header true, delimiter E'|', NULL '');\n")
		template += os.path.join(f"COPY gnaf.address_mesh_block_2011 FROM '{PSV_FOLDERS_DIR}Standard", f"{STATE}_ADDRESS_MESH_BLOCK_2011_psv.psv' WITH (format csv, header true, delimiter E'|', NULL '');\n")
		template += os.path.join(f"COPY gnaf.address_mesh_block_2016 FROM '{PSV_FOLDERS_DIR}Standard", f"{STATE}_ADDRESS_MESH_BLOCK_2016_psv.psv' WITH (format csv, header true, delimiter E'|', NULL '');\n")
		template += os.path.join(f"COPY gnaf.address_site_geocode FROM '{PSV_FOLDERS_DIR}Standard", f"{STATE}_ADDRESS_SITE_GEOCODE_psv.psv' WITH (format csv, header true, delimiter E'|', NULL '');\n")
		template += os.path.join(f"COPY gnaf.address_site FROM '{PSV_FOLDERS_DIR}Standard", f"{STATE}_ADDRESS_SITE_psv.psv' WITH (format csv, header true, delimiter E'|', NULL '');\n")
		template += os.path.join(f"COPY gnaf.locality_alias FROM '{PSV_FOLDERS_DIR}Standard", f"{STATE}_LOCALITY_ALIAS_psv.psv' WITH (format csv, header true, delimiter E'|', NULL '');\n")
		template += os.path.join(f"COPY gnaf.locality_neighbour FROM '{PSV_FOLDERS_DIR}Standard", f"{STATE}_LOCALITY_NEIGHBOUR_psv.psv' WITH (format csv, header true, delimiter E'|', NULL '');\n")
		template += os.path.join(f"COPY gnaf.locality_point FROM '{PSV_FOLDERS_DIR}Standard", f"{STATE}_LOCALITY_POINT_psv.psv' WITH (format csv, header true, delimiter E'|', NULL '');\n")
		template += os.path.join(f"COPY gnaf.locality FROM '{PSV_FOLDERS_DIR}Standard", f"{STATE}_LOCALITY_psv.psv' WITH (format csv, header true, delimiter E'|', NULL '');\n")
		template += os.path.join(f"COPY gnaf.mb_2011 FROM '{PSV_FOLDERS_DIR}Standard", f"{STATE}_MB_2011_psv.psv' WITH (format csv, header true, delimiter E'|', NULL '');\n")
		template += os.path.join(f"COPY gnaf.mb_2016 FROM '{PSV_FOLDERS_DIR}Standard", f"{STATE}_MB_2016_psv.psv' WITH (format csv, header true, delimiter E'|', NULL '');\n")
		template += os.path.join(f"COPY gnaf.primary_secondary FROM '{PSV_FOLDERS_DIR}Standard", f"{STATE}_PRIMARY_SECONDARY_psv.psv' WITH (format csv, header true, delimiter E'|', NULL '');\n")
		template += os.path.join(f"COPY gnaf.state FROM '{PSV_FOLDERS_DIR}Standard", f"{STATE}_STATE_psv.psv' WITH (format csv, header true, delimiter E'|', NULL '');")
		template += os.path.join(f"COPY gnaf.street_locality_alias FROM '{PSV_FOLDERS_DIR}Standard", f"{STATE}_STREET_LOCALITY_ALIAS_psv.psv' WITH (format csv, header true, delimiter E'|', NULL '');\n")
		template += os.path.join(f"COPY gnaf.street_locality_point FROM '{PSV_FOLDERS_DIR}Standard", f"{STATE}_STREET_LOCALITY_POINT_psv.psv' WITH (format csv, header true, delimiter E'|', NULL '');\n")
		template += os.path.join(f"COPY gnaf.street_locality FROM '{PSV_FOLDERS_DIR}Standard", f"{STATE}_STREET_LOCALITY_psv.psv' WITH (format csv, header true, delimiter E'|', NULL '');\n")

		with open(f'standard_tables_load_{STATE}.sql', 'w+') as f:
			f.write(template)


if __name__ == '__main__':
	create_authority_codes_sql_file(PSV_FOLDERS_DIR)
	create_state_sql_files(PSV_FOLDERS_DIR)

-- DROP VIEW gnaf.address_mesh_block_2011_view;

CREATE OR REPLACE VIEW gnaf.address_mesh_block_2011_view AS
 SELECT a.address_mesh_block_2011_pid,
    a.address_detail_pid,
    a.mb_2011_pid,
    b.mb_2011_code,
    a.mb_match_code
   FROM gnaf.address_mesh_block_2011 a,
    gnaf.mb_2011 b
  WHERE a.mb_2011_pid::text = b.mb_2011_pid::text;

-- DROP VIEW gnaf.address_mesh_block_2016_view;

CREATE OR REPLACE VIEW gnaf.address_mesh_block_2016_view AS 
 SELECT a.address_mesh_block_2016_pid,
    a.address_detail_pid,
    a.mb_2016_pid,
    b.mb_2016_code,
    a.mb_match_code
   FROM gnaf.address_mesh_block_2016 a,
    gnaf.mb_2016 b
  WHERE a.mb_2016_pid::text = b.mb_2016_pid::text;

-- DROP VIEW gnaf.address_site_geocode_view;

CREATE OR REPLACE VIEW gnaf.address_site_geocode_view AS 
 SELECT a.address_site_geocode_pid,
    a.address_site_pid,
    a.latitude,
    a.longitude,
    b.name AS geocode_type
   FROM gnaf.address_site_geocode a,
    gnaf.geocode_type_aut b
  WHERE a.geocode_type_code::text = b.code::text;

-- DROP VIEW gnaf.address_view;

CREATE OR REPLACE VIEW gnaf.address_view AS 
 SELECT ad.address_detail_pid,
    ad.street_locality_pid,
    ad.locality_pid,
    ad.building_name,
    ad.lot_number_prefix,
    ad.lot_number,
    ad.lot_number_suffix,
    fta.name AS flat_type,
    ad.flat_number_prefix,
    ad.flat_number,
    ad.flat_number_suffix,
    lta.name AS level_type,
    ad.level_number_prefix,
    ad.level_number,
    ad.level_number_suffix,
    ad.number_first_prefix,
    ad.number_first,
    ad.number_first_suffix,
    ad.number_last_prefix,
    ad.number_last,
    ad.number_last_suffix,
    sl.street_name,
    sl.street_class_code,
    sca.name AS street_class_type,
    sl.street_type_code,
    sl.street_suffix_code,
    ssa.name AS street_suffix_type,
    l.locality_name,
    st.state_abbreviation,
    ad.postcode,
    adg.latitude,
    adg.longitude,
    gta.name AS geocode_type,
    ad.confidence,
    ad.alias_principal,
    ad.primary_secondary,
    ad.legal_parcel_id,
    ad.date_created
   FROM gnaf.address_detail ad
     LEFT JOIN gnaf.flat_type_aut fta ON ad.flat_type_code::text = fta.code::text
     LEFT JOIN gnaf.level_type_aut lta ON ad.level_type_code::text = lta.code::text
     JOIN gnaf.street_locality sl ON ad.street_locality_pid::text = sl.street_locality_pid::text
     LEFT JOIN gnaf.street_suffix_aut ssa ON sl.street_suffix_code::text = ssa.code::text
     LEFT JOIN gnaf.street_class_aut sca ON sl.street_class_code = sca.code
     LEFT JOIN gnaf.street_type_aut sta ON sl.street_type_code::text = sta.code::text
     JOIN gnaf.locality l ON ad.locality_pid::text = l.locality_pid::text
     JOIN gnaf.address_default_geocode adg ON ad.address_detail_pid::text = adg.address_detail_pid::text
     LEFT JOIN gnaf.geocode_type_aut gta ON adg.geocode_type_code::text = gta.code::text
     LEFT JOIN gnaf.geocoded_level_type_aut glta ON ad.level_geocoded_code = glta.code
     JOIN gnaf.state st ON l.state_pid::text = st.state_pid::text
  WHERE ad.confidence > CAST(CAST('-1' AS integer) AS numeric);
-- DROP VIEW gnaf.locality_view;

CREATE OR REPLACE VIEW gnaf.locality_view AS 
 SELECT a.locality_name,
    b.latitude,
    b.longitude,
    c.name AS geocode_type,
    a.locality_pid,
    a.state_pid
   FROM gnaf.locality a,
    gnaf.locality_point b,
    gnaf.geocode_type_aut c
  WHERE a.locality_pid::text = b.locality_pid::text AND c.code::text = 'LOC'::text;

-- DROP VIEW gnaf.street_view;

CREATE OR REPLACE VIEW gnaf.street_view AS 
 SELECT a.street_name,
    a.street_type_code,
    a.street_suffix_code,
    b.latitude,
    b.longitude,
    c.name AS geocode_type,
    a.locality_pid,
    a.street_locality_pid
   FROM gnaf.street_locality a LEFT JOIN
    gnaf.street_locality_point b INNER JOIN gnaf.geocode_type_aut c ON c.code::text = 'STL'::text
  ON a.street_locality_pid::text = b.street_locality_pid::text;

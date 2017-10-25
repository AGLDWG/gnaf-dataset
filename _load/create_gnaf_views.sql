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
 SELECT a.address_detail_pid,
    a.street_locality_pid,
    a.locality_pid,
    a.number_first,
    b.street_name,
    b.street_type_code,
    c.locality_name,
    d.state_abbreviation,
    a.postcode,
    e.longitude,
    e.latitude,
    f.name AS geocode_type,
    a.confidence
   FROM gnaf.address_detail a,
    gnaf.street_locality b,
    gnaf.locality c,
    gnaf.state d,
    gnaf.address_default_geocode e,
    gnaf.geocode_type_aut f
  WHERE a.street_locality_pid::text = b.street_locality_pid::text AND b.locality_pid::text = c.locality_pid::text AND c.state_pid::text = d.state_pid::text AND a.address_detail_pid::text = e.address_detail_pid::text AND e.geocode_type_code::text = f.code::text;

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

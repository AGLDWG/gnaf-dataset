DROP TABLE STREET_LOCALITY_POINT;
DROP TABLE PRIMARY_SECONDARY;
DROP TABLE ADDRESS_MESH_BLOCK_2016;
DROP TABLE ADDRESS_SITE_GEOCODE;
DROP TABLE LOCALITY_ALIAS;
DROP TABLE LOCALITY_POINT;
DROP TABLE ADDRESS_MESH_BLOCK_2011;
DROP TABLE ADDRESS_ALIAS;
DROP TABLE LOCALITY_NEIGHBOUR;
DROP TABLE ADDRESS_DEFAULT_GEOCODE;
DROP TABLE STREET_LOCALITY_ALIAS;
DROP TABLE MB_2016;
DROP TABLE ADDRESS_DETAIL;
DROP TABLE MB_MATCH_CODE_AUT;
DROP TABLE MB_2011;
DROP TABLE STREET_LOCALITY_ALIAS_TYPE_AUT;
DROP TABLE LOCALITY_ALIAS_TYPE_AUT;
DROP TABLE GEOCODE_TYPE_AUT;
DROP TABLE ADDRESS_ALIAS_TYPE_AUT;
DROP TABLE PS_JOIN_TYPE_AUT;
DROP TABLE GEOCODED_LEVEL_TYPE_AUT;
DROP TABLE STREET_LOCALITY;
DROP TABLE ADDRESS_SITE;
DROP TABLE LEVEL_TYPE_AUT;
DROP TABLE FLAT_TYPE_AUT;
DROP TABLE STREET_TYPE_AUT;
DROP TABLE LOCALITY;
DROP TABLE STREET_CLASS_AUT;
DROP TABLE STREET_SUFFIX_AUT;
DROP TABLE ADDRESS_TYPE_AUT;
DROP TABLE LOCALITY_CLASS_AUT;
DROP TABLE STATE;
DROP TABLE GEOCODE_RELIABILITY_AUT;





CREATE TABLE gnaf.ADDRESS_ALIAS (
 address_alias_pid varchar(15) NOT NULL,
 date_created date NOT NULL,
 date_retired date,
 principal_pid varchar(15) NOT NULL,
 alias_pid varchar(15) NOT NULL,
 alias_type_code varchar(10) NOT NULL,
 alias_comment varchar(200)
);

CREATE TABLE gnaf.ADDRESS_ALIAS_TYPE_AUT (
 code varchar(10) NOT NULL,
 name varchar(50) NOT NULL,
 description varchar(30)
);

CREATE TABLE gnaf.ADDRESS_DEFAULT_GEOCODE (
 address_default_geocode_pid varchar(15) NOT NULL,
 date_created date NOT NULL,
 date_retired date,
 address_detail_pid varchar(15) NOT NULL,
 geocode_type_code varchar(4) NOT NULL,
 longitude numeric(11,8),
 latitude numeric(10,8)
);

CREATE TABLE gnaf.ADDRESS_DETAIL (
 address_detail_pid varchar(15) NOT NULL,
 date_created date NOT NULL,
 date_last_modified date,
 date_retired date,
 building_name varchar(45),
 lot_number_prefix varchar(2),
 lot_number varchar(5),
 lot_number_suffix varchar(2),
 flat_type_code varchar(7),
 flat_number_prefix varchar(2),
 flat_number numeric(5),
 flat_number_suffix varchar(2),
 level_type_code varchar(4),
 level_number_prefix varchar(2),
 level_number numeric(3),
 level_number_suffix varchar(2),
 number_first_prefix varchar(3),
 number_first numeric(6),
 number_first_suffix varchar(2),
 number_last_prefix varchar(3),
 number_last numeric(6),
 number_last_suffix varchar(2),
 street_locality_pid varchar(15),
 location_description varchar(45),
 locality_pid varchar(15) NOT NULL,
 alias_principal char(1),
 postcode varchar(4),
 private_street varchar(75),
 legal_parcel_id varchar(20),
 confidence numeric(1),
 address_site_pid varchar(15) NOT NULL,
 level_geocoded_code numeric(2) NOT NULL,
 property_pid varchar(15),
 gnaf_property_pid varchar(15),
 primary_secondary varchar(1)
);

CREATE TABLE gnaf.ADDRESS_MESH_BLOCK_2011 (
 address_mesh_block_2011_pid varchar(15) NOT NULL,
 date_created date NOT NULL,
 date_retired date,
 address_detail_pid varchar(15) NOT NULL,
 mb_match_code varchar(15) NOT NULL,
 mb_2011_pid varchar(15) NOT NULL
);

CREATE TABLE gnaf.ADDRESS_MESH_BLOCK_2016 (
 address_mesh_block_2016_pid varchar(15) NOT NULL,
 date_created date NOT NULL,
 date_retired date,
 address_detail_pid varchar(15) NOT NULL,
 mb_match_code varchar(15) NOT NULL,
 mb_2016_pid varchar(15) NOT NULL
);

CREATE TABLE gnaf.ADDRESS_SITE (
 address_site_pid varchar(15) NOT NULL,
 date_created date NOT NULL,
 date_retired date,
 address_type varchar(8),
 address_site_name varchar(45)
);

CREATE TABLE gnaf.ADDRESS_SITE_GEOCODE (
 address_site_geocode_pid varchar(15) NOT NULL,
 date_created date NOT NULL,
 date_retired date,
 address_site_pid varchar(15),
 geocode_site_name varchar(46),
 geocode_site_description varchar(45),
 geocode_type_code varchar(4),
 reliability_code numeric(1) NOT NULL,
 boundary_extent numeric(7),
 planimetric_accuracy numeric(12),
 elevation numeric(7),
 longitude numeric(11,8),
 latitude numeric(10,8)
);

CREATE TABLE gnaf.ADDRESS_TYPE_AUT (
 code varchar(8) NOT NULL,
 name varchar(50) NOT NULL,
 description varchar(30)
);

CREATE TABLE gnaf.FLAT_TYPE_AUT (
 code varchar(7) NOT NULL,
 name varchar(50) NOT NULL,
 description varchar(30)
);

CREATE TABLE gnaf.GEOCODED_LEVEL_TYPE_AUT (
 code numeric(2) NOT NULL,
 name varchar(50) NOT NULL,
 description varchar(70)
);

CREATE TABLE gnaf.GEOCODE_RELIABILITY_AUT (
 code numeric(1) NOT NULL,
 name varchar(50) NOT NULL,
 description varchar(100)
);

CREATE TABLE gnaf.GEOCODE_TYPE_AUT (
 code varchar(4) NOT NULL,
 name varchar(50) NOT NULL,
 description varchar(250)
);

CREATE TABLE gnaf.LEVEL_TYPE_AUT (
 code varchar(4) NOT NULL,
 name varchar(50) NOT NULL,
 description varchar(30)
);

CREATE TABLE gnaf.LOCALITY (
 locality_pid varchar(15) NOT NULL,
 date_created date NOT NULL,
 date_retired date,
 locality_name varchar(100) NOT NULL,
 primary_postcode varchar(4),
 locality_class_code char(1) NOT NULL,
 state_pid varchar(15) NOT NULL,
 gnaf_locality_pid varchar(15),
 gnaf_reliability_code numeric(1) NOT NULL
);

CREATE TABLE gnaf.LOCALITY_ALIAS (
 locality_alias_pid varchar(15) NOT NULL,
 date_created date NOT NULL,
 date_retired date,
 locality_pid varchar(15) NOT NULL,
 name varchar(100) NOT NULL,
 postcode varchar(4),
 alias_type_code varchar(10) NOT NULL,
 state_pid varchar(15) NOT NULL
);

CREATE TABLE gnaf.LOCALITY_ALIAS_TYPE_AUT (
 code varchar(10) NOT NULL,
 name varchar(50) NOT NULL,
 description varchar(100)
);

CREATE TABLE gnaf.LOCALITY_CLASS_AUT (
 code char(1) NOT NULL,
 name varchar(50) NOT NULL,
 description varchar(200)
);

CREATE TABLE gnaf.LOCALITY_NEIGHBOUR (
 locality_neighbour_pid varchar(15) NOT NULL,
 date_created date NOT NULL,
 date_retired date,
 locality_pid varchar(15) NOT NULL,
 neighbour_locality_pid varchar(15) NOT NULL
);

CREATE TABLE gnaf.LOCALITY_POINT (
 locality_point_pid varchar(15) NOT NULL,
 date_created date NOT NULL,
 date_retired date,
 locality_pid varchar(15) NOT NULL,
 planimetric_accuracy numeric(12),
 longitude numeric(11,8),
 latitude numeric(10,8)
);

CREATE TABLE gnaf.MB_2011 (
 mb_2011_pid varchar(15) NOT NULL,
 date_created date NOT NULL,
 date_retired date,
 mb_2011_code varchar(15) NOT NULL
);

CREATE TABLE gnaf.MB_2016 (
 mb_2016_pid varchar(15) NOT NULL,
 date_created date NOT NULL,
 date_retired date,
 mb_2016_code varchar(15) NOT NULL
);

CREATE TABLE gnaf.MB_MATCH_CODE_AUT (
 code varchar(15) NOT NULL,
 name varchar(100) NOT NULL,
 description varchar(250)
);

CREATE TABLE gnaf.PRIMARY_SECONDARY (
 primary_secondary_pid varchar(15) NOT NULL,
 primary_pid varchar(15) NOT NULL,
 secondary_pid varchar(15) NOT NULL,
 date_created date NOT NULL,
 date_retired date,
 ps_join_type_code numeric(2) NOT NULL,
 ps_join_comment varchar(500)
);

CREATE TABLE gnaf.PS_JOIN_TYPE_AUT (
 code numeric(2) NOT NULL,
 name varchar(50) NOT NULL,
 description varchar(500)
);

CREATE TABLE gnaf.STATE (
 state_pid varchar(15) NOT NULL,
 date_created date NOT NULL,
 date_retired date,
 state_name varchar(50) NOT NULL,
 state_abbreviation varchar(3) NOT NULL
);

CREATE TABLE gnaf.STREET_CLASS_AUT (
 code char(1) NOT NULL,
 name varchar(50) NOT NULL,
 description varchar(200)
);

CREATE TABLE gnaf.STREET_LOCALITY (
 street_locality_pid varchar(15) NOT NULL,
 date_created date NOT NULL,
 date_retired date,
 street_class_code char(1) NOT NULL,
 street_name varchar(100) NOT NULL,
 street_type_code varchar(15),
 street_suffix_code varchar(15),
 locality_pid varchar(15) NOT NULL,
 gnaf_street_pid varchar(15),
 gnaf_street_confidence numeric(1),
 gnaf_reliability_code numeric(1) NOT NULL
);

CREATE TABLE gnaf.STREET_LOCALITY_ALIAS (
 street_locality_alias_pid varchar(15) NOT NULL,
 date_created date NOT NULL,
 date_retired date,
 street_locality_pid varchar(15) NOT NULL,
 street_name varchar(100) NOT NULL,
 street_type_code varchar(15),
 street_suffix_code varchar(15),
 alias_type_code varchar(10) NOT NULL
);

CREATE TABLE gnaf.STREET_LOCALITY_ALIAS_TYPE_AUT (
 code varchar(10) NOT NULL,
 name varchar(50) NOT NULL,
 description varchar(15)
);

CREATE TABLE gnaf.STREET_LOCALITY_POINT (
 street_locality_point_pid varchar(15) NOT NULL,
 date_created date NOT NULL,
 date_retired date,
 street_locality_pid varchar(15) NOT NULL,
 boundary_extent numeric(7),
 planimetric_accuracy numeric(12),
 longitude numeric(11,8),
 latitude numeric(10,8)
);

CREATE TABLE gnaf.STREET_SUFFIX_AUT (
 code varchar(15) NOT NULL,
 name varchar(50) NOT NULL,
 description varchar(30)
);

CREATE TABLE gnaf.STREET_TYPE_AUT (
 code varchar(15) NOT NULL,
 name varchar(50) NOT NULL,
 description varchar(15)
);





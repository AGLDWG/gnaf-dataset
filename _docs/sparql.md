# SPARQL Service
The GNAF LDAPI supports a SPARQL service endpoint at <http://gnafld.net/sparql>. This service can be used to query the RDF graph version of the GNAF data, as opposed to the Postgres version of the data which is queried by the Linked Data API. the graph version is kept in sync with the Postgres version by being emptied and rebuilt on every Postgres verson's release.

## Service description
The capabilities of the SPARQL endpoint are described with metadata in accordance with the [SPARQL 1.1 Service Description](https://www.w3.org/TR/sparql11-service-description/). The service's metadata about its endpoints, functions and other details - such as whether it is read/write or read only - can be retrieved from <http://gnafld.net/sparql> using an HTTP GET request without any query parameter strings. As per Linked Data norms, the metadata formatted in RDF can be accessed with an Accept header set to an RDF MIME format (e.g. `text/turtle` or `application/rdf_xml`) and an HTML version can be accessed with an Accept header of `text/html`, which is the default. You can visit the service endpoint using a normal web browser to see the HTML version and the RDF version, in the rutle format, is reproduced below:

```
@prefix rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix sd:   <http://www.w3.org/ns/sparql-service-description#> .
@prefix sdf:  <http://www.w3.org/ns/formats/> .
@prefix void: <http://rdfs.org/ns/void#> .
@prefix xsd:  <http://www.w3.org/2001/XMLSchema#> .

<http://gnafld.net/sparql>
    a                       sd:Service ;
    sd:endpoint             <http://gnafld.net/sparql> ;
    sd:supportedLanguage    sd:SPARQL11Query ; # yes, read only!
    sd:resultFormat         sdf:SPARQL_Results_JSON ;  # we only deliver JSON results, sorry!
    sd:feature sd:DereferencesURIs ;
    sd:defaultDataset [ # there are no Named Graphs within this triplestore
        a sd:Dataset ;
        sd:defaultGraph [
            a sd:Graph ;
            void:triples "286779722"^^xsd:integer # yes, more than 286 million triples!
        ]
    ]
.```


## Example queries
This query gets all the aliases of an Address (ADDRESS_X) and the Alias type:

```
PREFIX gnaf: <http://gnafld.net/def/gnaf#>
SELECT ?aliasAddress ?aliasType
WHERE {
    <ADDRESS_X>
      gnaf:hasAlias [
        gnaf:aliasOf  ?aliasAddress .
        a             ?aliasType .
      ]
}```

For the Address <http://gnafld.net/address/GAACT714875297>, this returns:

`?aliasType = <http://gnafld.net/address/GAACT715708026>`
and  
`?aliasAddress = <http://gnafld.net/def/gnaf#RangedAddressAlias>`
so we can understand that the original address and the alias address are about a large block with one Address having a first and Last street number and the other having just one number.


## How to lodge queries
SPARQL queries like the above can be put to this GNAF SPARQL service according to the

# GNAF LDAPI test
A Linked Data API for PSMA's G-NAF.


## About
This code is a test Linked Data API for the delivery of the contents of the [G-NAF, the Geocoded National Address File](https://www.psma.com.au/products/g-naf) from [PSMA](https://www.psma.com.au/) according to [Linked Data](https://en.wikipedia.org/wiki/Linked_data) and [Semantic Web](https://www.w3.org/standards/semanticweb/) principles.

The data accessed is the copy of the G-NAF available freely on the [data.gov.au/](http://data.gov.au/) catalogue: 

* <http://data.gov.au/dataset/geocoded-national-address-file-g-naf>
    * downloaded on 2017-08-18

This code is written to test out Linked Data ideas with the G-NAF and may not be used in a final product. 

### API technical details 
This code uses a simple Linked Data API that reads data from a data source, in this case a Postgres database containing the GNAF data, restructures it according to various models, such as addressing ontologies, and the delivers it in either human- or machine-readable forms. 

Constraints on the API's views and formats are imposed via the LDAPI module housed within the _ldpai folder.

The API uses Python Flask as it's HTTP framework and Jinja2 for HTML generation by templates. RDF generation is done by generating triples using the Python rdflib module. 


## License
This code repository licensed using Creative Commons 4.0 International (see [LICENSE file](LICENSE)).


## Contacts
Programmer:  
**Nicholas Car**  
*Data Architect*  
Geoscience Australia  
<nicholas.car@ga.gov.au>  
<http://orcid.org/0000-0002-8742-7730>

Programmer:  
**Joseph Abhayaratna**  
*Chief Technical Officer*  
PSMA Australia Ltd.
<Joseph.Abhayaratna@psma.com.au>  

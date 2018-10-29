# GNAF Linked Data dataset
A Linked Data version of PSMA's G-NAF dataset.


## About
### API
This code builds a API to delivery the contents of the [G-NAF, the Geocoded National Address File](https://www.psma.com.au/products/g-naf)
from [PSMA](https://www.psma.com.au/) on the web, according to [Linked Data](https://en.wikipedia.org/wiki/Linked_data)
and [Semantic Web](https://www.w3.org/standards/semanticweb/) principles. This code makes heavy use of the
[Python pyLDAPI module](https://pypi.org/project/pyldapi/) which is based on Python's well-known
[Flask](http://flask.pocoo.org/) web API framework.

The data accessed is the copy of the G-NAF available freely on the [data.gov.au/](http://data.gov.au/) catalogue:

* <http://data.gov.au/dataset/geocoded-national-address-file-g-naf>
    * downloaded on 2018-06-01

### Data model
This API delivers the GNAF data according to the [GNAF ontology](http://linked.data.gov.au/def/gnaf) which is a Semantic
Web data model using the [Web Ontology Language, OWL](https://www.w3.org/OWL/). This set theory-based modelling language
creates graph models of data connecting all elements, *nodes*, via *edges*, which in OWL are typed relationships.


## Use
Go to the landing page of the dataset, [http://linked.data.gov.au/dataset/gnaf](http://linked.data.gov.au/dataset/gnaf) and
navigate the various lists of objects, service end points etc. from there.


## License
This code is licensed using the GPL v3 (see the [LICENSE file](LICENSE) for the deed).


## Contacts
Product Owner:
**Joseph Abhayaratna**  
*Chief Technical Officer*  
PSMA Australia Ltd.
<Joseph.Abhayaratna@psma.com.au>  

Developer:  
**Nicholas Car**  
*Senior Experimental Scientist*  
CSIRO Land & Water  
<nicholas.car@csiro.au>  
<http://orcid.org/0000-0002-8742-7730>  

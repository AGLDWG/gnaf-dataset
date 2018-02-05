import rdflib

g = rdflib.Graph()
g.load('/Users/car587/work/gnaf-ont/codes/StreetSubclasses.ttl', format='turtle')
q = '''
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    SELECT *
    WHERE {
        ?uri    rdfs:subClassOf skos:Concept ;
                skos:altLabel ?code .
    }
'''
for r in g.query(q):
    print("'" + str(r['code']) + "': '" + str(r['uri']) + "',")

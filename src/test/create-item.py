#! /root/anaconda3/envs/wikibase/bin/python

from wikibaseintegrator.models import Qualifiers, References, Reference
from wikibaseintegrator import WikibaseIntegrator
from wikibaseintegrator import wbi_login
from wikibaseintegrator import datatypes
from wikibaseintegrator.wbi_config import config as wbi_config

def setup_config():
    """
    Set up WBI config to use local docker installation
    """
    wbi_config['MEDIAWIKI_API_URL'] = 'http://139.144.66.193:8181/api.php'
    wbi_config['SPARQL_ENDPOINT_URL'] = '"http://139.144.66.193:8282/proxy/wdqs/bigdata/namespace/wdq/sparql"'
    wbi_config['WIKIBASE_URL'] = 'http://wikibase.svc'
    # wbi_config['MEDIAWIKI_API_URL'] = 'http://localhost/api.php'
    # wbi_config['SPARQL_ENDPOINT_URL'] = '"http://localhost:8282/proxy/wdqs/bigdata/namespace/wdq/sparql"'
    # wbi_config['WIKIBASE_URL'] = 'http://wikibase.svc'

def main():
    """
    main() function for wikibase integration
    """
    # WikibaseIntegrator uses "Wikidata" as default endpoint. 
    # To use another instance of Wikibase instead, you can override the wbi_config module.
    setup_config()

    # Default variables
    WDUSER, WDPASS = "Admin", "90J8XXXaO4Sr9^^Z"
    # WDUSER, WDPASS = "Mohammadzainabbas", "fHh!%shFa6^h"

    # Create login and WikibaseIntegrator object
    login = wbi_login.Login(user=WDUSER, password=WDPASS)
    wbi = WikibaseIntegrator(login=login)

    # Create an item
    new_item = wbi.item.new()
    new_item.labels.set('en', 'NTTData test item')
    new_item.labels.set('es', 'Elemento de prueba de NTTData')

    new_item.aliases.set('en', 'Item')
    new_item.aliases.set('es', 'Ítem')

    new_item.descriptions.set('en', 'A freshly created element')
    new_item.descriptions.set('es', 'Un elemento recién creado')

    # Create a claim, with qualifiers and references, and add it to the new item entity
    new_qualifiers = Qualifiers()
    new_qualifiers.add(datatypes.String(prop_nr='P828', value='Item qualifier'))

    new_references = References()
    new_reference1 = Reference()
    new_reference1.add(datatypes.String(prop_nr='P828', value='Item string reference'))

    new_reference2 = Reference()
    new_reference2.add(datatypes.String(prop_nr='P828', value='Another item string reference'))

    new_references.add(new_reference1)
    new_references.add(new_reference2)

    new_claim = datatypes.String(prop_nr='P31533', value='A String property', qualifiers=new_qualifiers, references=new_references)

    new_item.claims.add(new_claim)

    # Write to wikibase instance
    new_item.write()



if __name__ == "__main__":
    main()

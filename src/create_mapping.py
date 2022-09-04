#! /root/anaconda3/envs/wikibase/bin/python

from wikibaseintegrator.models import Qualifiers, References, Reference
from wikibaseintegrator import WikibaseIntegrator
from wikibaseintegrator import wbi_login
from wikibaseintegrator import datatypes
from wikibaseintegrator.wbi_config import config as wbi_config
from os.path import join, isfile, exists, isdir, abspath, pardir
from os import listdir, getcwd
import pandas as pd
from wikibaseintegrator.datatypes import (URL, CommonsMedia, ExternalID, Form, GeoShape, GlobeCoordinate, Item, Lexeme, Math, MonolingualText, MusicalNotation, Property, Quantity, Sense, String, TabularData, Time)
from wikibaseintegrator.wbi_enums import ActionIfExists, WikibaseDatePrecision, WikibaseRank, WikibaseSnakType
from wikibaseintegrator.wbi_exceptions import MissingEntityException, ModificationFailed, MWApiError

def setup_config():
    """
    Set up WBI config to use local docker installation
    """
    wbi_config['MEDIAWIKI_API_URL'] = 'http://139.144.66.193:8181/api.php'
    wbi_config['SPARQL_ENDPOINT_URL'] = '"http://139.144.66.193:8282/proxy/wdqs/bigdata/namespace/wdq/sparql"'
    wbi_config['WIKIBASE_URL'] = 'http://wikibase.svc'

def create_mapping(file_name, wbi):
    """
    Create mapping for all columns
    """
    # Read .csv file to create mappings
    __df = pd.read_csv(join(file_name))
    
    if __df.empty: return

    columns_with_mappings = list(__df.T.to_dict().values())
    __mapping = list()

    for item in columns_with_mappings:
        __col_name = item['column']
        __data_type = item['data_type']
        __type = item['type']
        __mapping_code = item['mapping_code']
        __description = item['description']
        __alias = item['alias']

        try:

            p = wbi.property.new(datatype=__data_type)
            p.labels.set('en', __col_name)
            p.descriptions.set('en', __description)
            p.aliases.set('en', __alias)

            res = p.write()

            ident = [x for x in str(res).split('\n') if "_id='P" in x]
            if len(ident) == 1:
                prop_code = ident[0].split("'")[1]
                __mapping.append(dict({ "column": __col_name, "prop": prop_code }))
                print("Column '{}' is mapped to '{}'".format(__col_name, prop_code))
            else:
                raise Exception("Surprise, this method didn't work.")
        
        except ModificationFailed as e:
            print("Property '{}' already exists".format(__col_name))
            continue
    return __mapping

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

    parent_dir = abspath(join(getcwd(), pardir))
    data_dir = join(parent_dir, "data")
    team_mapping = join(data_dir, "team_mapping.csv")
    project_mapping = join(data_dir, "project_mapping.csv")

    # Create login and WikibaseIntegrator object
    login = wbi_login.Login(user=WDUSER, password=WDPASS)
    wbi = WikibaseIntegrator(login=login)

    __team_mapping = create_mapping(team_mapping, wbi)
    __project_mapping = create_mapping(project_mapping, wbi)

    __mapping = __team_mapping + __project_mapping

    with open(join(data_dir, "column_mapping.txt")) as f:
        # save list to a pickle file
        pickle.dump(__mapping, f)


if __name__ == "__main__":
    main()

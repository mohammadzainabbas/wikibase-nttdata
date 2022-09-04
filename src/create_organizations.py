#! /root/anaconda3/envs/wikibase/bin/python

from wikibaseintegrator.models import Qualifiers, References, Reference
from wikibaseintegrator import WikibaseIntegrator
from wikibaseintegrator import wbi_login
from wikibaseintegrator import datatypes
from wikibaseintegrator.wbi_config import config as wbi_config
from os.path import join, isfile, exists, isdir, abspath, pardir
from os import PathLike, listdir, getcwd
import pandas as pd
from wikibaseintegrator.datatypes import (URL, CommonsMedia, ExternalID, Form, GeoShape, GlobeCoordinate, Item, Lexeme, Math, MonolingualText, MusicalNotation, Property, Quantity, Sense, String, TabularData, Time)
from wikibaseintegrator.wbi_enums import ActionIfExists, WikibaseDatePrecision, WikibaseRank, WikibaseSnakType, WikibaseDatatype
from wikibaseintegrator.wbi_exceptions import MissingEntityException, ModificationFailed, MWApiError
import pickle

def print_log(text: str) -> None:
    """
    Print log
    """
    print("[ log ] {}".format(text))

def print_error(text: str) -> None:
    """
    Print error
    """
    print("[ error ] {}".format(text))

def setup_config():
    """
    Set up WBI config to use local docker installation
    """
    wbi_config['MEDIAWIKI_API_URL'] = 'http://139.144.66.193:8181/api.php'
    wbi_config['SPARQL_ENDPOINT_URL'] = '"http://139.144.66.193:8282/proxy/wdqs/bigdata/namespace/wdq/sparql"'
    wbi_config['WIKIBASE_URL'] = 'http://wikibase.svc'

def convert_to_wikibase_datatype(__value, __propcode, data_type):
    """
    Convert and return Wikibase datatype
    """
    if __data_type == WikibaseDatatype.STRING:
        return String(value=__value, prop_nr=__propcode)
    elif (__data_type == "item") or (__data_type == WikibaseDatatype.ITEM):
        return Item(value=__value, prop_nr=__propcode)
    elif __data_type == WikibaseDatatype.QUANTITY:
        return Quantity(value=__value, prop_nr=__propcode)
    elif __data_type == WikibaseDatatype.TIME:
        return Time(value=__value, prop_nr=__propcode)
    elif __data_type == WikibaseDatatype.URL:
        return URL(value=__value, prop_nr=__propcode)
    elif __data_type == WikibaseDatatype.COMMONSMEDIA:
        return CommonsMedia(value=__value, prop_nr=__propcode)
    elif (__data_type == "externalId") or (__data_type == WikibaseDatatype.EXTERNALID):
        return ExternalID(value=__value, prop_nr=__propcode)
    elif (__data_type == "form") or (__data_type == WikibaseDatatype.FORM):
        return Form(value=__value, prop_nr=__propcode)
    elif (__data_type == "geoShape") or (__data_type == WikibaseDatatype.GEOSHAPE):
        return GeoShape(value=__value, prop_nr=__propcode)
    elif (__data_type == "globeCoordinate") or (__data_type == WikibaseDatatype.GLOBECOORDINATE):
        return GlobeCoordinate(value=__value, prop_nr=__propcode)
    elif (__data_type == "lexeme") or (__data_type == WikibaseDatatype.LEXEME):
        return Lexeme(value=__value, prop_nr=__propcode)
    elif __data_type == WikibaseDatatype.MATH:
        return Math(value=__value, prop_nr=__propcode)
    elif (__data_type == "monolingualText") or (__data_type == WikibaseDatatype.MONOLINGUALTEXT):
        return MonolingualText(value=__value, prop_nr=__propcode)
    elif (__data_type == "musicalNotation") or (__data_type == WikibaseDatatype.MUSICALNOTATION):
        return MusicalNotation(value=__value, prop_nr=__propcode)
    elif (__data_type == "property") or (__data_type == WikibaseDatatype.PROPERTY):
        return Property(value=__value, prop_nr=__propcode)
    elif (__data_type == "sense") or (__data_type == WikibaseDatatype.SENSE):
        return Sense(value=__value, prop_nr=__propcode)
    elif (__data_type == "tabularData") or (__data_type == WikibaseDatatype.TABULARDATA):
        return TabularData(value=__value, prop_nr=__propcode)
    else:
        print_error("Invalid data type for property: '{}'".format(__propcode))

def create_organization(data: dict, mapping: list, wbi: WikibaseIntegrator) -> None:
    """
    Create mapping for all columns
    """
    __key = list(data.keys())[0]
    __props = list(data[__key].keys())

    item = wbi.item.new()
    item.labels.set("en", __key)
    item.aliases.set("en", __key)
    item.descriptions.set("en", __key)

    for prop in __props:
        if prop not in mapping:
            print_error("Unable to find mapping for {}".format(prop))
            continue

        __mapping = mapping[prop]

        __value = data[__key][prop]
        __propcode = __mapping["prop"]

        __data_type = __mapping["data_type"]

        

            item.set_claim(__propcode, String(__value))




    print_log("Creating mapping for {}".format(file_name))
    # Read .csv file to create mappings
    __df = pd.read_csv(join(file_name))
    
    if __df.empty: return list()

    columns_with_mappings = list(__df.T.to_dict().values())
    __mapping = list()

    for item in columns_with_mappings:
        __col_name = item['column']
        __data_type = item['data_type']
        __description = item['description']
        __alias = item['alias'].split(";")

        try:

            p = wbi.property.new(datatype=__data_type)
            p.labels.set('en', __col_name)
            p.descriptions.set('en', __description)
            p.aliases.set('en', __alias)

            res = p.write()

            ident = [x for x in str(res).split('\n') if "_id='P" in x]
            if len(ident) == 1:
                prop_code = ident[0].split("'")[1]
                __mapping.append(dict({ "column": __col_name, "prop": prop_code, "data_type": __data_type }))
                print_log("Column '{}' is mapped to '{}'".format(__col_name, prop_code))
            else:
                raise Exception("Surprise, this method didn't work.")
        
        except ModificationFailed as e:
            print_error("Property '{}' already exists".format(__col_name))
            continue
    return __mapping

def main() -> None:
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

    parent_dir = abspath(join(getcwd(), pardir))
    data_dir = join(parent_dir, "data")
    project_data = join(data_dir, "BDMA_Projects_v1.csv")
    column_mapping_data = join(data_dir, "column_mapping.csv")
    
    df = pd.read_csv(column_mapping_data)
    column_mapping = df.set_index("column").T.to_dict()

    __columns = ["Client Type", "Client"]
    __df = pd.read_csv(project_data, usecols=__columns).drop_duplicates()
    __data = __df.set_index("Client").T.to_dict()

    if isinstance(__data, dict):
        # only one item
        create_organization(__data, column_mapping, wbi)
    elif isinstance(__data, list):
        for item in __data:
            create_organization(item, column_mapping, wbi)
    else:
        print_error("Unexpected data type")







    mapping_files = ['team_member_mapping.csv', 'project_mapping.csv', 'organization_mapping.csv', 'task_mapping.csv']
    __mapping = list()
    for file in mapping_files:
        __mapping.extend(create_mapping(join(data_dir, file), wbi))

    #save mapping to .csv file   
    pd.DataFrame(__mapping).to_csv(join(data_dir, "column_mapping.csv"), index=False)

if __name__ == "__main__":
    main()

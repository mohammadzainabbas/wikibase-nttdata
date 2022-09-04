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

def convert_to_wikibase_datatype(__value, __propcode, __data_type):
    """
    Convert and return Wikibase datatype
    """
    if __data_type == WikibaseDatatype.STRING.value:
        return String(value=__value, prop_nr=__propcode)
    elif (__data_type == "item") or (__data_type == WikibaseDatatype.ITEM.value):
        return Item(value=__value, prop_nr=__propcode)
    elif __data_type == WikibaseDatatype.QUANTITY.value:
        return Quantity(value=__value, prop_nr=__propcode)
    elif __data_type == WikibaseDatatype.TIME.value:
        return Time(value=__value, prop_nr=__propcode)
    elif __data_type == WikibaseDatatype.URL.value:
        return URL(value=__value, prop_nr=__propcode)
    elif __data_type == WikibaseDatatype.COMMONSMEDIA.value:
        return CommonsMedia(value=__value, prop_nr=__propcode)
    elif (__data_type == "externalId") or (__data_type == WikibaseDatatype.EXTERNALID.value):
        return ExternalID(value=__value, prop_nr=__propcode)
    elif (__data_type == "form") or (__data_type == WikibaseDatatype.FORM.value):
        return Form(value=__value, prop_nr=__propcode)
    elif (__data_type == "geoShape") or (__data_type == WikibaseDatatype.GEOSHAPE.value):
        return GeoShape(value=__value, prop_nr=__propcode)
    elif (__data_type == "globeCoordinate") or (__data_type == WikibaseDatatype.GLOBECOORDINATE.value):
        return GlobeCoordinate(value=__value, prop_nr=__propcode)
    elif (__data_type == "lexeme") or (__data_type == WikibaseDatatype.LEXEME.value):
        return Lexeme(value=__value, prop_nr=__propcode)
    elif __data_type == WikibaseDatatype.MATH.value:
        return Math(value=__value, prop_nr=__propcode)
    elif (__data_type == "monolingualText") or (__data_type == WikibaseDatatype.MONOLINGUALTEXT.value):
        return MonolingualText(value=__value, prop_nr=__propcode)
    elif (__data_type == "musicalNotation") or (__data_type == WikibaseDatatype.MUSICALNOTATION.value):
        return MusicalNotation(value=__value, prop_nr=__propcode)
    elif (__data_type == "property") or (__data_type == WikibaseDatatype.PROPERTY.value):
        return Property(value=__value, prop_nr=__propcode)
    elif (__data_type == "sense") or (__data_type == WikibaseDatatype.SENSE.value):
        return Sense(value=__value, prop_nr=__propcode)
    elif (__data_type == "tabularData") or (__data_type == WikibaseDatatype.TABULARDATA.value):
        return TabularData(value=__value, prop_nr=__propcode)
    else:
        print_error("Invalid data type for property: '{}'".format(__propcode))

def create_project(data: dict, mapping: list, wbi: WikibaseIntegrator) -> dict:
    """
    Create mapping for all columns
    """
    __key = list(data.keys())[0]
    __props = list(data[__key].keys())

    item = wbi.item.new()
    item.labels.set("en", __key)
    item.aliases.set("en", __key)
    item.descriptions.set("en", "An project named {}".format(__key))

    __res = dict({ "item": __key })

    for prop in __props:
        if prop not in mapping:
            print_error("Unable to find mapping for {}".format(prop))
            continue

        __mapping = mapping[prop]

        __value = data[__key][prop]
        __propcode = __mapping["prop"]
        __data_type = __mapping["data_type"]

        __claim = convert_to_wikibase_datatype(__value, __propcode, __data_type)
        item.claims.add(__claim)
    
    print_log("Creating item for '{}'".format(__key))

    try:
        res = item.write()
        prop_code = res.get_json()['id']
        __res["prop"] = prop_code
        print_log("Key '{}' is mapped to '{}'".format(__key, prop_code))
    except ModificationFailed as e:
        print_error("Unable to create item for '{}'".format(__key))
        print_error(e)
    return __res

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

    # parent_dir = abspath(join(getcwd(), pardir))
    parent_dir = join("/root", "wikibase-nttdata")
    data_dir = join(parent_dir, "data")
    project_data = join(data_dir, "BDMA_Projects_v1.csv")
    column_mapping_data = join(data_dir, "column_mapping.csv")
    items_data = join(data_dir, "items.csv")
    
    df = pd.read_csv(column_mapping_data)
    column_mapping = df.set_index("column").T.to_dict()

    __columns = ["Project", "Project Type", "Client"]
    __df = pd.read_csv(project_data, usecols=__columns).drop_duplicates()
    __data = __df.set_index("Client").T.to_dict()

    __res = list()
    if exists(items_data):
        __df = pd.read_csv(items_data)
        __res = __df.to_dict(orient="records")

    if isinstance(__data, dict):
        # only one item
        __res.append(create_project(__data, column_mapping, wbi))
    elif isinstance(__data, list):
        for item in __data:
            __res.append(create_project(item, column_mapping, wbi))
    else:
        print_error("Unexpected data type")

    pd.DataFrame(__res).to_csv(items_data, index=False)

if __name__ == "__main__":
    main()

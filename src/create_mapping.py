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
    team_data = join(data_dir, "BDMA_Team_v1.csv")
    project_data = join(data_dir, "BDMA_Projects_v1.csv")

    # Create login and WikibaseIntegrator object
    login = wbi_login.Login(user=WDUSER, password=WDPASS)
    wbi = WikibaseIntegrator(login=login)


if __name__ == "__main__":
    main()

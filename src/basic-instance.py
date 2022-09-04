#! /root/anaconda3/envs/wikibase/bin/python
from wikibaseintegrator.wbi_config import config as wbi_config

if __name__ == "__main__":

    wbi_config['MEDIAWIKI_API_URL'] = 'http://localhost/api.php'
    wbi_config['SPARQL_ENDPOINT_URL'] = '"http://localhost:8282/proxy/wdqs/bigdata/namespace/wdq/sparql"'
    wbi_config['WIKIBASE_URL'] = 'http://wikibase.svc'

#! /root/anaconda3/envs/wikibase/bin/python
from wikibaseintegrator import WikibaseIntegrator

if __name__ == "__main__":

    wbi = WikibaseIntegrator()
    my_first_wikidata_item = wbi.item.get(entity_id='Q5')

    # to check successful installation and retrieval of the data, you can print the json representation of the item
    print(my_first_wikidata_item.get_json())
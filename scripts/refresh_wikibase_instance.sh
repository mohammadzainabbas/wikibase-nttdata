#! /bin/bash

cd ~/wikibase

docker-compose -f docker-compose.new.yml down 

docker volume prune

docker-compose -f docker-compose.new.yml up -d 

cd -
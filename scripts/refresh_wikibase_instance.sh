#! /bin/bash

cd ~/wikibase

docker-compose -f docker-compose.new.yml down 

docker volume prune -y

docker-compose -f docker-compose.new.yml up -d 

cd -
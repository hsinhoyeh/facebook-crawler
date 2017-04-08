#!/bin/bash
pwd=$(pwd)
docker run \
    -d \
    -v $pwd/init:/docker-entrypoint-initdb.d \
    -p 3306:3306 \
    -e MYSQL_ROOT_PASSWORD=jfd889a2jk \
    mysql:5.7

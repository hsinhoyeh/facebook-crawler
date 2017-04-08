#!/bin/bash

user=user1
db=FacebookDB
dsn=mysql://$user@127.0.0.1:3306/$db?charset=utf8
fbToken="<secret-access-token>"

dsn=$dsn fbToken=$fbToken python3 get_groups.py

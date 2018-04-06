#!/usr/bin/python

import requests
es_host = 'localhost'
endpoint = 'http://' + es_host + ':9200' + '/_template/tmpl-megacorp'

schema = '''{
"template" : "megacorp*",
"mappings" : {
"megacorp" : {
"dynamic" : "strict",
"_all" : { "enabled": false },
"_source": { "enabled": true },
"properties" : {
    "first_name": {"type" : "string", "index" : "analyzed"},
    "last_name": {"type": "string", "index" : "analyzed"},
    "age": {"type": "integer"},
    "about": {"type" : "string", "index" : "analyzed"},
    "interests": {"type" : "string", "index": "analyzed"},
    "SrcFile": {"type" : "string", "index" : "analyzed"}
}}}}'''

response = requests.put(endpoint, data=schema)
res = response.text

print "======================"
print res

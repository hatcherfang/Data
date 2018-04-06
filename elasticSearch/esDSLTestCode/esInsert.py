'''refer url:http://xiaorui.cc/2014/09/16/%E4%BD%BF%E7%94%A8python%E6%93%8D%E4%BD%9Celasticsearch%E5%AE%9E%E7%8E%B0%E7%9B%91%E6%8E%A7%E6%95%B0%E6%8D%AE%E5%8F%8Akibana%E5%88%86%E6%9E%90/'''

from elasticsearch import Elasticsearch
import json
es = Elasticsearch(hosts=[{'host': 'localhost', 'port': 9200}])
m_Index = "megacorp"
es.indices.create(index=m_Index, ignore=400)
dataBody = {
    "first_name" : "John",
    "last_name" :  "Smith",
    "age" :        25,
    "about" :      "I love to go rock climbing",
    "interests": [ "sports", "music" ]
}
dataBody2 = {
    "first_name" :  "Jane",
    "last_name" :   "Smith",
    "age" :         32,
    "about" :       "I like to collect rock albums",
    "interests":  [ "music" ]
}
dataBody3 = {
    "first_name" :  "Douglas",
    "last_name" :   "Fir",
    "age" :         35,
    "about":        "I like to build cabinets",
    "interests":  [ "forestry" ]
}
print es.index(index=m_Index, doc_type='employee', id=3, body=dataBody3)

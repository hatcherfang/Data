from elasticsearch import Elasticsearch
import json
client = Elasticsearch()
m_Index = "megacorp"
m_Index2 = "blogs"
m_Index3 = "iws-rawloginteger-2016-10-13"
m_Index4 = "iws-stats-log-integer-2016-10-28"
m_Body = {
  "aggs": {
    "all_interests": {
      "terms": { "field": "interests" }
    }
  }
}

m_Body2 = {
  "query": {
    "match": {
      "last_name": "smith"
    }
  },
  "aggs": {
    "all_interests": {
      "terms": {
        "field": "interests"
      }
    }
  }
}

m_Body3 = {
    "aggs" : {
        "all_interests" : {
            "terms" : { "field" : "interests" },
            "aggs" : {
                "avg_age" : {
                    "avg" : { "field" : "age" }
                }
            }
        }
    }
}

m_Body4 = {
   "settings" : {
      "number_of_shards" : 3,
      "number_of_replicas" : 1
   }
}

m_Body5 = {
    "query" : {
        "match" : {
            "about" : "rock climbing"
        }
    }
}

m_Body6 = {
    "query" : {
        "match_phrase" : {
            "about" : "rock climbing"
        }
    },
    "highlight": {
        "fields" : {
            "about" : {}
        }
    }
}
#aggregation for field CLF_B2
m_Body7 = {
    "aggs": {
            "count": {"sum": {"field": "CLF_B2"}}
    }
}
#query filter time range
m_Body8 = {
    "query": {
        "bool":{
                 "filter":
                  [{
                    "range":
                          {
                            "CLF_Timestamp":
                            {
                               "from": 1477534760,
                               "to": 1477645560
                            }
                          }
                   },
                   {
                     "term":
                          {
                            "CLF_B1":1
                          }
                   }
                  ]
        }
    },
    "aggs": {
        "CLF_B1": {
            "sum": {
                 "field": "CLF_B1"
            }
        }
    }
}

m_Body81 = {
    "query":{
        "filtered":
        {
        "range":
         {
            "CLF_Timestamp":
             {
                "gte":0
             }
         }
    }
}
    # "aggs":
    # {
    #   "CLF_Timestamp":
    #     {
    #       "avg": {"field": "CLF_Timestamp"}
    #     }
    # }

}
m_Body9 = {
 "size": 1,
 "fields": [
 "CLF_Timestamp"
 ]
}

m_Body10 = {
    # specific the timestamp range and using field1 and field2 to do aggs and
    # then get the top hits 2(size:2)
    "size": 0,
    "query": {
           "range": {
               "CLF_UTCTimeStamp":
               {
                   "gte": "timeStart",
                   "lt": "timeEnd"
                 }
             }
    },
    "aggs": {
           "duplicate_count": {
               "terms": {
                   "field": "field1",
                   "min_doc_count": 2
               },
               "aggs": {
                   "duplicate_log": {
                       "terms": {
                           "field": "field2",
                           "min_doc_count": 2
                       },
                       "aggs": {
                           # get the raw documents top 2
                           "duplicateDocuments": {
                               "top_hits": {
                                   "size": 2
                               }
                           }

                       }
                   }
                   }
            }
    }
}

response = client.search(index=m_Index4, body=m_Body8)
print json.dumps(response, indent=4)
print '-------------------------------------------------'
#print json.dumps(response["aggregations"], indent=4, sort_keys=True)

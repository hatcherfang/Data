# ES akey
ES_AKEY=""

# ES skey
ES_SKEY=""

# ES host ip
es_host = ""

# ES index
es_index = ''

# ES region name
es_region = ""

# query time range from start timestamp*1000 to end timestamp*1000
timeStart = xxx
timeEnd = xxx

# time interval
# 86400*1000 equal to one day
# timeInterval = 86400*1000
timeInterval = 3600*1000

# CLF_ID in sqlite db table
CLF_ID =
srcFile = ""

m_Body = {
    "size":0,
    "query":{
           "bool": {
               "filter":
               [
                {
                   "range":{
                       "CLF_UTCTimeStamp":
                       {
                           "gte": timeStart,
                           "lt": timeEnd
                         }
                     }
                }
               ]
           }
    },
    "aggs":{
           "duplicate_count":{
               "terms": {
                   "field": "srcFile"
               },
               "aggs":{
                   "duplicate_log":{
                       "terms": {
                           "field": "CLF_ID",
                           "min_doc_count": 2,
                           "size": 0
                       }
                   }
                   }
            }
    }
}

m_Body1 = {
    "size": 0,
    "query": {
        "bool": {
            "filter":
            [
             {
              "range":
                     {
                       "CLF_UTCTimeStamp":
                       {
                          "gte": timeStart,
                          "lt": timeEnd
                       }
                     }
             },
             {
              "term":
                    {
                     "srcFile": srcFile
                    }
             }
            ]
      }
    },
    "aggs":{
        "duplicate_count": {
           "terms": {
               "field": "srcFile"
           },
           "aggs": {
               "duplicate_log":{
                  "terms":
                        {
                         "field": "CLF_ID",
                         "min_doc_count": 2,
                         "size": 0
                        }
                }
          }
       }
    }
}

m_Body2 = {
    "size": 0,
    "query": {
        "bool": {
            "filter":
            [
             {
              "range":
                     {
                       "CLF_UTCTimeStamp":
                       {
                          "gte": timeStart,
                          "lt": timeEnd
                       }
                     }
             },
             {
              "term":
                    {
                     "CLF_ID": CLF_ID
                    }
             }
            ]
      }
    },
    "aggs":{
        "duplicate_count": {
           "terms": {
               "field": "CLF_ID",
               "min_doc_count": 2
           },
           "aggs": {
               "duplicate_fileCount":{
                  "terms":
                        {
                         "field": "srcFile",
                         "min_doc_count": 2
                        },
                       "aggs": {
                           "duplicationCount": {
                               "top_hits": {
                                 "size": 4
                               }
                           }
                       }
                }
          }
       }
   }
}

m_Body3 = {
    "size":0,
    "query":{
           "bool": {
               "filter":
               [
                {
                   "range":{
                       "CLF_UTCTimeStamp":
                       {
                           "gte": timeStart,
                           "lt": timeEnd
                         }
                     }
                },
                {
                 "term":
                       {
                        "CLF_ID": CLF_ID
                       }
                }
               ]
           }
    },
    "aggs":{
           "duplicate_count":{
               "terms": {
                   "field": "CLF_ID",
                   "min_doc_count": 2
               },
               "aggs":{
                   "duplicate_log":{
                       "terms": {
                           "field": "srcFile",
                           "min_doc_count": 2
                       }
                   }
                   }
            }
    }
}
m_Body4 = {
    "size": 100,
    "query": {
        "bool": {
            "filter":
            [
             {
              "range":
                     {
                       "CLF_UTCTimeStamp":
                       {
                          "gte": timeStart,
                          "lt": timeEnd
                       }
                     }
             },
             {
              "term":
                    {
                     "srcFile": srcFile
                    }
             },
             {
              "term":
                    {
                     "CLF_ID": 1
                    }
             },
            ]
      }
    }
 }

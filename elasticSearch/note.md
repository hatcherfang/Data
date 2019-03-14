## docker start ES  
docker run --name myes -d -p 9200:9200 -p 9300:9300 0d8b5016c399
access elasticsearch-head plugin `http://{你的ip地址}:9200/_plugin/head/`  
# Convert SQL to DSL  
eg:  
SQL:  
```
select log_id, count(log_id) as chat_num , sum(`server`), avg(chat_msg) from tableName group by role_id limit 10
```
mapping DSL:  
```
{
    "from": 0,
    "size": 0,
    "_source": {
        "includes": [
            "log_id",
            "COUNT",
            "SUM",
            "AVG"
        ],
        "excludes": []
    },
    "stored_fields": "log_id",
    "aggregations": {
        "role_id": {
            "terms": {
                "field": "role_id",
                "size": 10,
                "shard_size": 2000,
                "min_doc_count": 1,
                "shard_min_doc_count": 0,
                "show_term_doc_count_error": false,
                "order": [
                    {
                        "_count": "desc"
                    },
                    {
                        "_key": "asc"
                    }
                ]
            },
            "aggregations": {
                "chat_num": {
                    "value_count": {
                        "field": "log_id"
                    }
                },
                "SUM(`server`)": {
                    "sum": {
                        "field": "`server`"
                    }
                },
                "AVG(chat_msg)": {
                    "avg": {
                        "field": "chat_msg"
                    }
                }
            }
        }
    }
}
```


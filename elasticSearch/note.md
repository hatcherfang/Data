### docker start ES  
docker run --name myes -d -p 9200:9200 -p 9300:9300 0d8b5016c399
access elasticsearch-head plugin `http://{你的ip地址}:9200/_plugin/head/`  
### Convert SQL to DSL  
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
### Search note    
1. 精确查找(term)  
term是一种简单的词条查询，它不会分析所查询的词，只是简单返回完全匹配的结果.  
2. 简单模糊查询(match)  
match将查询的词以某种分析器（可自己指定）分析，然后构建相应查询。  
总之重要的是，经match查询的词条是经过分析的,这一点至关重要。   
让我们来查文章内容中包含“笔记”内容的文章。  
```
curl localhost:9200/posts/article/_search -d @search.json

{
    "query": {
        "match": {
            "contents": "笔记"
        }
    }
}
```
```
{
    "hits": [{
        "_index": "posts",
        "_type": "article",
        "_id": "2",
        "_score": 0.44194174,
        "_source": {
            "id": 2,
            "name": "javascript笔记",
            "author": "wthfeng",
            "date": "2016-10-23",
            "contents": "这是我的javascript学习笔记"
        }
    }, {
        "_index": "posts",
        "_type": "article",
        "_id": "1",
        "_score": 0.13561106,
        "_source": {
            "id": 1,
            "name": "Ealsticesarch笔记",
            "author": "wthfeng",
            "date": "2016-10-25",
            "contents": "这是我的ES学习笔记"
        }
    }, {
        "_index": "posts",
        "_type": "article",
        "_id": "3",
        "_score": 0.13561106,
        "_source": {
            "id": 3,
            "name": "java笔记",
            "author": "wthfeng",
            "date": "2016-10-23",
            "contents": "这是我的java学习笔记"
        }
    }, {
        "_index": "posts",
        "_type": "article",
        "_id": "5",
        "_score": 0.014065012,
        "_source": {
            "id": 5,
            "name": "生活日志",
            "author": "wthfeng",
            "date": "2015-09-21",
            "contents": "这是日常生活的记录"
        }
    }]

}
```

这样就可以模糊查询数据了，不过有个问题是，我查询关键词是“笔记”，  
为何id为5的文章会出现？因为它有一个“记”字。  
ES的词条分析查询其实不完全等同于SQL中的模糊查询。ES的查询有相关性，用查询得分（_score）表示。  
相关性高的排在前面，低的排在后面，id为5的文章只有一个字匹配，所以排在最后。  
具体查询相关知识下篇讲解，现在我们知道个大概即可。

match查询有几个参数控制匹配行为，如operator，接受值or和and表示。指示关键词是以或的形式连接还是和的形式。  
如上例，我们想要完全匹配“笔记”的查询结果，需要这样：  
```
{
  "query": {
    "match": {
      "contents": {
        "query":"笔记",
        "operator":"and"
      }
    }
  }
}
```
如此即可查询包含“笔记”的文章。它的效果类似于:  
```
select * from article where contents like '%笔记%' 
```
此处亲测叙述有误：  
1. match operator 组合只是提高匹配精度, operator=and 表示单词组合都必须在句子里面出现，并不需要连续，
跟sql里的 '%keyword%'并不类似。    
2. match_phrase 才是把一个词整体去做匹配  
3. 查询数量(search_type=count)  
用于查询符合结果的文档数而不是文档内容。需使用search_type指定为count。  
```
curl ‘localhost:9200/posts/article/_search?pretty&search_type=count’ -d @search.json

{
    "query":{
        "match":{
            "name":"笔记"
        }
    }   
}
```
结果为：  
```
{
  "took" : 4,
  "timed_out" : false,
  "_shards" : {
    "total" : 5,
    "successful" : 5,
    "failed" : 0
  },
  "hits" : {
    "total" : 3,
    "max_score" : 0.0,
    "hits" : [ ]
  }
}
```
total 字段为3，表明查询结果为3。  

4. 更新文档（POST）:局部更新，全部更新    
ES中的更新总是这样：先删除旧文档，再插入新文档。  
因为文档一旦在倒排索引中存储，就不能被更改。  
无论是局部更新还是完全替换，都必须走先删除后插入的流程。（ES内部是这样，不过你不用关注这个过程）。  
5. 删除文档(DELETE)   

### [xpack 插件使用](https://discuss.elastic.co/t/x-pack-6-3-sql-query/137765/2)  
eg:  
```
POST /_xpack/sql?format=txt
{
    "query": "select * from \"your index name\" limit 10"
}
```

### Reference  
[ElasticSearch DSL](https://elasticsearch-dsl.readthedocs.io/en/latest/search_dsl.html)  

## Study confluent kafka-rest plugin  
### [Confluent introduce](https://my.oschina.net/guol/blog/822980)  
Confluent是由LinkedIn开发出Apache Kafka的团队成员，基于这项技术创立了新公司Confluent，  
Confluent的产品也是围绕着Kafka做的。    
### [kafka-rest github](https://github.com/confluentinc/kafka-rest)  
### [kafka-rest docker image](https://hub.docker.com/r/confluentinc/cp-kafka-rest)  
### [Confluent REST Proxy API Reference](https://docs.confluent.io/current/kafka-rest/docs/api.html)  
### [configure kafka-rest connecting kafka](https://blog.csdn.net/wild46cat/article/details/79137485)  
```
docker run -d \
  --net=host \
  --name=kafka-rest \
  -e KAFKA_REST_ZOOKEEPER_CONNECT=ai-02:2181 \
  -e KAFKA_REST_LISTENERS=http://10.240.228.198:8082 \
  -e KAFKA_REST_HOST_NAME=10.240.228.198 \
  confluentinc/cp-kafka-rest
```
note:  
KAFKA_REST_ZOOKEEPER_CONNECT: the zookeeper that you want to connect  
KAFKA_REST_LISTENERS: localhost ip  
## Reference  

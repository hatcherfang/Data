## About Kafka   
Kafka 是一个分布式的，高吞吐量，易于扩展地基于主题发布/订阅的消息系统，最早是由 Linkedin 开发，并于 2011 年开源并贡献给 Apache 软件基金会。一般来说，Kafka 有以下几个典型的应用场景:  
  
- 作为消息队列。由于 Kafka 拥有高吞吐量，并且内置消息主题分区，备份，容错等特性，使得它更适合使用在大规模，高强度的消息数据处理的系统中。  
- 流计算系统的数据源。流数据产生系统作为 Kafka 消息数据的生产者将数据流分发给 Kafka 消息主题，流数据计算系统 (Storm,Spark Streaming 等) 实时消费并计算数据。这也是本文将要介绍的应用场景。  
- 系统用户行为数据源。这种场景下，系统将用户的行为数据，如访问页面，停留时间，搜索日志，感兴趣的话题等数据实时或者周期性的发布到 Kafka 消息主题，作为对接系统数据的来源。  
- 日志聚集。Kafka 可以作为一个日志收集系统的替代解决方案，我们可以将系统日志数据按类别汇集到不同的 Kafka 消息主题中。  
- 事件源。在基于事件驱动的系统中，我们可以将事件设计成合理的格式，作为 Kafka 消息数据存储起来，以便相应系统模块做实时或者定期处理。由于 Kafka 支持大数据量存储，并且有备份和容错机制，所以可以让事件驱动型系统更加健壮和高效。  

## About Spark Steaming  

Spark Streaming 模块是对于 Spark Core 的一个扩展，目的是为了以高吞吐量，并且容错的方式处理持续性的数据流。目前 Spark Streaming 支持的外部数据源有 Flume、 Kafka、Twitter、ZeroMQ、TCP Socket 等。  
Discretized Stream 也叫 DStream 是 Spark Streaming 对于持续数据流的一种基本抽象，在内部实现上，DStream 会被表示成一系列连续的 RDD(弹性分布式数据集)，每一个 RDD 都代表一定时间间隔内到达的数据。所以在对 DStream 进行操作时，会被 Spark Stream 引擎转化成对底层 RDD 的操作。对 Dstream 的操作类型有:  
  
- Transformations: 类似于对 RDD 的操作，Spark Streaming 提供了一系列的转换操作去支持对 DStream 的修改。如 map,union,filter,transform 等  
- Window Operations: 窗口操作支持通过设置窗口长度和滑动间隔的方式操作数据。常用的操作有 reduceByWindow,reduceByKeyAndWindow,window 等  
- Output Operations: 输出操作允许将 DStream 数据推送到其他外部系统或存储平台, 如 HDFS, Database 等，类似于 RDD 的 Action 操作，Output 操作也会实际上触发对 DStream 的转换操作。常用的操作有 print,saveAsTextFiles,saveAsHadoopFiles, foreachRDD 等。  
  
## Kafka 集群搭建步骤  
(hatcher注: 前提spark cluster已经搭建好，所以不再考虑 zookeeper的搭建)
1. wget http://mirrors.tuna.tsinghua.edu.cn/apache/kafka/1.0.0/kafka_2.12-1.0.0.tgz  
2. tar –xvf kafka_2.12-1.0.0.tgz  
3. 编辑 Kafka 配置文件  
3.1 编辑 config/server.properties 文件  
添加或修改以下配置。  
Kafka Broker 配置项  
```  
broker.id=0  
port=9092  
host.name=192.168.1.1  
zookeeper.contact=192.168.1.1:2181,192.168.1.2:2181,192.168.1.3:2181  
log.dirs=/home/fams/kafka-logs  
```  
这些配置项解释如下：  
- broker.id：Kafka broker 的唯一标识，集群中不能重复。  
- port: Broker 的监听端口，用于监听 Producer 或者 Consumer 的连接。  
- host.name:当前 Broker 服务器的 IP 地址或者机器名。  
- zookeeper.contact:Broker 作为 zookeeper 的 client，可以连接的 zookeeper 的地址信息。  
- log.dirs：日志保存目录。  
  
3.2 编辑 config/producer.properties 文件  
添加或者修改以下配置：  
Kafka Producer 配置项  
```  
broker.list=192.168.1.1:9092,192.168.1.2:9092,192.168.1.3:9092  
producer.type=async  
```  
这些配置项解释如下：  
broker.list：集群中 Broker 地址列表。  
producer.type: Producer 类型,async 异步生产者，sync 同步生产者。  
  
3.3 编辑 config/consumer.properties 文件  
Kafka Consumer 配置项  
```  
zookeeper.contact=192.168.1.1:2181,192.168.1.2:2181,192.168.1.3:2181  
```  
配置项解释如下：  
zookeeper.contact: Consumer 可以连接的 zookeeper 服务器地址列表。  
4. 上传修改好的安装包到其他机器  
至此，我们已经在 192.168.1.1 机器上修改好了所有需要的配置文件，那么接下来请用以下命令打包该 Kafka 安装包，并上传至 192.168.1.2 和 192.168.1.3 两台机器上。  
5. 启动 Kafka 服务   
分别在三台机器上运行下面命令启动 Kafka 服务。  
```  
nohup bin/kafka-server-start.sh config/server.properties &  
```  
6. 验证安装  
我们的验证步骤有两个。  
  
第一步，分别在三台机器上使用下面命令查看是否有 Kafka。   
```  
ps –ef | grep kafka  
```  
第二步，创建消息主题，并通过 console producer 和 console consumer 验证消息可以被正常的生产和消费。  
```  
bin/kafka-topics.sh --create \  
--replication-factor 3 \  
--partitions 3 \  
--topic user-behavior-topic \  
--zookeeper 192.168.1.1:2181,192.168.1.2:2181,192.168.1.3:2181  
```  
运行下面命令打开打开 console producer。  
```  
bin/kafka-console-producer.sh --broker-list 192.168.1.1:9092 --topic user-behavior-topic  
```  
在另一台机器打开 console consumer。  
```  
./kafka-console-consumer.sh --zookeeper 192.168.1.2:2181 --topic user-behavior-topic --from-beginning  
```  
  
然后如果在 producer console 输入一条消息，能从 consumer console 看到这条消息就代表安装是成功的。  

查看topic命令:  
`./bin/kafka-topics.sh --describe --zookeeper sm:2181,sd1:2181,sd2:2181 --topic user-behavior-topic`  
  
## Reference  
- [Spark 实战, 第 2 部分:使用 Kafka 和 Spark Streaming 构建实时数据处理系统](https://www.ibm.com/developerworks/cn/opensource/os-cn-spark-practice2/index.html)  
- [Kafka官网](https://kafka.apache.org/)  
- [Kafka Quickstart](https://kafka.apache.org/quickstart)   
- [Spark Streaming Programing Guide](http://spark.apache.org/docs/latest/streaming-programming-guide.html)  
- [spark streaming + kafka +python(编程)初探](https://www.jianshu.com/p/04f8e78ea656)  
- [基于Python的Spark Streaming+Kafka编程实践](https://blog.csdn.net/eric_sunah/article/details/54096057)  

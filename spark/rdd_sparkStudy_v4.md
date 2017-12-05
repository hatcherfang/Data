### RDD依赖、窄宽依赖  

#### RDD依赖与DAG  

一系列转化操作形成RDD的有向无环图(DAG)，行动操作触发作业的提交与执行。每个RDD维护了其对直接父RDD(一个或多个)的依赖，其中包含了父RDD的引用和依赖类型信息，通过dependencies()我们可以获取对应RDD的依赖，其返回一个依赖列表。  

通过RDD的父RDD引用就可以从DAG上向前回溯找到其所有的祖先RDD。spark提供了toDebugString方法来查看RDD的谱系。对于如下一段简单的代码：  
```
val input = sc.parallelize(1 to 10)
val repartitioned = input.repartition(2)
val sum = repartitioned.sum
```
我们就可以通过在RDD上调用toDebugString来查看其依赖以及转化关系，结果如下：
```
// input.toDebugString
res0: String = (4) ParallelCollectionRDD[0] at parallelize at <console>:21 []

// repartitioned.toDebugString
res1: String =
(2) MapPartitionsRDD[4] at repartition at <console>:23 []
 |  CoalescedRDD[3] at repartition at <console>:23 []
 |  ShuffledRDD[2] at repartition at <console>:23 []
 +-(4) MapPartitionsRDD[1] at repartition at <console>:23 []
    |  ParallelCollectionRDD[0] at parallelize at <console>:21 []
```
上述repartitioned的依赖链存在两个缩进等级。同一缩进等级的转化操作构成一个Stage(阶段)，它们不需要混洗(shuffle)数据，并可以流水线执行(pipelining)。  

#### 窄依赖和宽依赖  

spark中RDD之间的依赖分为窄(Narrow)依赖和宽(Wide)依赖两种。我们先放出一张示意图：  
![wide_narrow_dep](http://smallx.me/2016/06/07/spark%E4%BD%BF%E7%94%A8%E6%80%BB%E7%BB%93/%E7%AA%84%E4%BE%9D%E8%B5%96%E5%92%8C%E5%AE%BD%E4%BE%9D%E8%B5%96.jpg)  
- **窄依赖**指父RDD的每一个分区最多被一个子RDD的分区所用，表现为一个父RDD的分区对应于一个子RDD的分区，或多个父RDD的分区对应于一个子RDD的分区。图中，map/filter和union属于第一类，对输入进行协同划分(co-partitioned)的join属于第二类。(记忆：是一个树形结构)  
- **宽依赖**指父RDD的每一个分区可以被多个子RDD分区所用，表现为一个父RDD的分区对应于多个子RDD的分区，或一个子RDD的分区对应于多个父RDD的分区。换言之，子RDD的分区依赖于父RDD的多个或所有分区,这是因为shuffle类操作(所以宽依赖又叫shuffle依赖)，如图中的groupByKey和未经协同划分的join。  

**窄依赖对优化很有利**。逻辑上，每个RDD的算子都是一个fork/join(此join非上文的join算子，而是指同步多个并行任务的barrier(路障))： 把计算fork到每个分区，算完后join，然后fork/join下一个RDD的算子。如果直接翻译到物理实现，是很不经济的：一是每一个RDD(即使 是中间结果)都需要物化到内存或存储中，费时费空间；二是join作为全局的barrier，是很昂贵的，会被最慢的那个节点拖死。如果子RDD的分区到父RDD的分区是窄依赖，就可以实施经典的fusion优化，把两个fork/join合为一个；如果连续的变换算子序列都是窄依赖，就可以把很多个fork/join并为一个，不但减少了大量的全局barrier，而且无需物化很多中间结果RDD，这将极大地提升性能。Spark把这个叫做**流水线(pipeline)优化**。关于流水线优化，从MapPartitionsRDD中compute()的实现就可以看出端倪，该compute方法只是对迭代器进行复合，复合就是嵌套，因此数据处理过程就是对每条记录进行同样的嵌套处理直接得出所需结果，而没有中间计算结果，同时也要注意：依赖过长将导致嵌套过深，从而可能导致栈溢出。  

转换算子序列一碰上shuffle类操作，宽依赖就发生了，流水线优化终止。在具体实现 中，DAGScheduler从当前算子往前回溯依赖图，一碰到宽依赖，就生成一个stage来容纳已遍历的算子序列。在这个stage里，可以安全地实施流水线优化。然后，又从那个宽依赖开始继续回溯，生成下一个stage。  

另外，宽窄依赖的划分对spark的容错也具有重要作用，参见本文容错机制部分。

#### DAG到任务的划分  

用户代码定义RDD的有向无环图，行动操作把DAG转译为执行计划，进一步生成任务在集群中调度执行。  

具体地说，RDD的一系列转化操作形成RDD的DAG，在RDD上调用行动操作将触发一个Job(作业)的运行，Job根据DAG中RDD之间的依赖关系(宽依赖/窄依赖，也即是否发生shuffle)的不同将DAG划分为多个Stage(阶段)，一个Stage对应DAG中的一个或多个RDD，一个Stage对应多个RDD是因为发生了流水线执行(pipelining)，一旦Stage划分出来，Task(任务)就会被创建出来并发给内部的调度器，进而分发到各个executor执行，一个Stage会启动很多Task，每个Task都是在不同的数据分区上做同样的事情(即执行同样的代码段)，Stage是按照依赖顺序处理的，而Task则是独立地启动来计算出RDD的一部分，一旦Job的最后一个Stage结束，一个行动操作也就执行完毕了。  

Stage分为两种：ShuffleMapStage和ResultStage。ShuffleMapStage是非最终stage，后面还有其他的stage，所以它的输出一定是需要shuffle并作为后续stage的输入。ShuffleMapStage的最后Task就是ShuffleMapTask。ResultStage是一个Job的最后一个Stage，直接生成结果或存储。ResultStage的最后Task就是ResultTask。一个Job含有一个或多个Stage，最后一个为ResultTask，其他都为ShuffleMapStage。  

#### RDD不能嵌套  

RDD嵌套是不被支持的，也即不能在一个RDD操作的内部再使用RDD。如果在一个RDD的操作中，需要访问另一个RDD的内容，你可以尝试join操作，或者将数据量较小的那个RDD广播(broadcast)出去。  

你同时也应该注意到：join操作可能是低效的，将其中一个较小的RDD广播出去然后再join可以避免不必要的shuffle，俗称“小表广播”。  

#### 使用其他分区数据  

由于RDD不能嵌套，这使得“在计算一个分区时，访问另一个分区的数据”成为一件困难的事情。那么有什么好的解决办法吗？请继续看。  

spark依赖于RDD这种抽象模型进行粗粒度的并行计算，一般情况下每个节点的每次计算都是针对单一记录，当然也可以使用 RDD.mapPartition 来对分区进行处理，但都限制在一个分区内(当然更是一个节点内)。  

spark的worker节点相互之间不能直接进行通信，如果在一个节点的计算中需要使用到另一个分区的数据，那么还是有一定的困难的。  

你可以将整个RDD的数据全部广播(如果数据集很大，这可不是好办法)，或者广播一些其他辅助信息；也可以从所有节点均可以访问到的文件(hdfs文件)或者数据库(关系型数据库或者hbase)中读取；更进一步或许你应该修改你的并行方案，使之满足“可针对拆分得到的小数据块进行并行的独立的计算，然后归并得到大数据块的计算结果”的MapReduce准则，在“划分大的数据，并行独立计算，归并得到结果”的过程中可能存在数据冗余之类的，但它可以解决一次性没法计算的大数据，并最终提高计算效率，hadoop和spark都依赖于MapReduce准则。  

### 对RDD进行分区  

#### 何时进行分区？  

spark程序可以通过控制RDD分区方式来减少通信开销。分区并不是对所有应用都是有好处的，如果给定RDD只需要被扫描一次，我们完全没有必要对其预先进行分区处理。**只有当数据集多次在诸如连接这种基于键的操作中使用时，分区才会有帮助，同时记得将分区得到的新RDD持久化哦**。  

更多的分区意味着更多的并行任务(Task)数。对于shuffle过程，如果分区中数据量过大可能会引起OOM，这时可以将RDD划分为更多的分区，这同时也将导致更多的并行任务。spark通过线程池的方式复用executor JVM进程，每个Task作为一个线程存在于线程池中，这样就减少了线程的启动开销，可以高效地支持单个executor内的多任务执行，这样你就可以放心地将任务数量设置成比该应用分配到的CPU cores还要多的数量了。  
#### 如何分区与分区信息  

在创建RDD的时候，可以指定分区的个数，如果没有指定，则分区个数是系统默认值，即该程序所分配到的CPU核心数。在Java/Scala中，你可以使用rdd.getNumPartitions(1.6.0+)或rdd.partitions.size()来获取分区个数。  

对基本类型RDD进行重新分区，可以通过repartition()函数，只需要指定重分区的分区数即可。repartition操作会引起shuffle，因此spark提供了一个优化版的repartition，叫做coalesce()，它允许你指定是否需要shuffle。在使用coalesce时，需要注意以下几个问题：  

- coalesce默认shuffle为false，这将形成窄依赖，例如我们将1000个分区重新分到100个中时，并不会引起shuffle，而是原来的10个分区合并形成1个分区。  
- 但是对于从很多个(比如1000个)分区重新分到很少的(比如1个)分区这种极端情况，数据将会分布到很少节点(对于从1000到1的重新分区，则是1个节点)上运行，完全无法开掘集群的并行能力，为了规避这个问题，可以设置shuffle为true。**由于shuffle可以分隔stage，这就保证了上一阶段stage中的任务仍是很多个分区在并行计算，不这样设置的话，则两个上下游的任务将合并成一个stage进行计算，这个stage便会在很少的分区中进行计算**。  
- 如果当前每个分区的数据量过大，需要将分区数量增加，以利于充分利用并行，这时我们可以设置shuffle为true。对于数据分布不均而需要重分区的情况也是如此。**spark默认使用hash分区器将数据重新分区**。  

对RDD进行预置的hash分区，需将RDD转换为RDD[(key,value)]类型，然后就可以通过隐式转换为PairRDDFunctions，进而可以通过如下形式将RDD哈希分区，HashPartitioner会根据RDD中每个(key,value)中的key得出该记录对应的新的分区号：  
```
PairRDDFunctions.partitionBy(new HashPartitioner(n))  
```

另外，spark还提供了一个范围分区器，叫做RangePartitioner。范围分区器争取将所有的分区尽可能分配得到相同多的数据，并且所有分区内数据的上界是有序的。  

一个RDD可能存在分区器也可能没有，我们可以通过RDD的partitioner属性来获取其分区器，它返回一个Option对象(RangePartitioner 分区器返回None, HashPartitioner分区器返回`Some(org.apache.spark.HashPartitioner@4)`)。  
eg:  
```
scala> coalesceRDD.partitioner
res154: Option[org.apache.spark.Partitioner] = None

scala> partitionHashRDD.partitioner
res121: Option[org.apache.spark.Partitioner] = Some(org.apache.spark.HashPartitioner@4)
```

#### 如何进行自定义分区  

spark允许你通过提供一个自定义的Partitioner对象来控制RDD的分区方式，这可以让你利用领域知识进一步减少通信开销。

要实现自定义的分区器，你需要继承Partitioner类，并实现下面三个方法即可：

numPartitions: 返回创建出来的分区数。
getPartition: 返回给定键的分区编号(0到numPartitions-1)。
equals: Java判断相等性的标准方法。这个方法的实现非常重要，spark需要用这个方法来检查你的分区器对象是否和其他分区器实例相同，这样spark才可以判断两个RDD的分区方式是否相同。

### Reference  
- [spark使用总结](http://smallx.me/2016/06/07/spark%E4%BD%BF%E7%94%A8%E6%80%BB%E7%BB%93/)   

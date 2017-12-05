### 关于shuffle  
#### Background  
在MapReduce框架中，shuffle是连接Map和Reduce之间的桥梁，Map的输出要用到Reduce中必须经过shuffle这个环节，shuffle的性能高低直接影响了整个程序的性能和吞吐量。Spark作为MapReduce框架的一种实现，自然也实现了shuffle的逻辑，本文就深入研究Spark的shuffle是如何实现的，有什么优缺点，与Hadoop MapReduce的shuffle有什么不同。  
### Shuffle  
Shuffle是MapReduce框架中的一个特定的phase，介于Map phase和Reduce phase之间，当Map的输出结果要被Reduce使用时，输出结果需要按key哈希，并且分发到每一个Reducer上去，这个过程就是shuffle。由于shuffle涉及到了磁盘的读写和网络的传输，因此shuffle性能的高低直接影响到了整个程序的运行效率。  

下面这幅图清晰地描述了MapReduce算法的整个流程，其中shuffle phase是介于Map phase和Reduce phase之间。  
![mapReduceProcess](http://jerryshao.me/img/2014-01-04-spark-shuffle/mapreduce-process.jpg)  
概念上shuffle就是一个沟通数据连接的桥梁，那么实际上shuffle这一部分是如何实现的的呢，下面我们就以Spark为例讲一下shuffle在Spark中的实现。  
### Spark Shuffle进化史  
先以图为例简单描述一下Spark中shuffle的整一个流程：  
![sparkShuffle](http://jerryshao.me/img/2014-01-04-spark-shuffle/spark-shuffle.png)  
- 首先每一个Mapper会根据Reducer的数量创建出相应的bucket，bucket的总数量是M×R，其中M是Map的个数，R是Reduce的个数。  
- 其次Mapper产生的结果会根据设置的partition算法填充到每个bucket中去。这里的partition算法是可以自定义的，当然默认的算法是根据key哈希到不同的bucket中去。  
- 当Reducer启动时，它会根据自己task的id和所依赖的Mapper的id从远端或是本地的block manager中取得相应的bucket作为Reducer的输入进行处理。  

这里的bucket是一个抽象概念，在实现中每个bucket可以对应一个文件，可以对应文件的一部分或是其他等。  

接下来我们分别从shuffle write和shuffle fetch这两块来讲述一下Spark的shuffle进化史。  

### Shuffle Write  
在Spark 0.6和0.7的版本中，对于shuffle数据的存储是以文件的方式存储在block manager中，与rdd.persist(StorageLevel.DISk_ONLY)采取相同的策略，可以参看：  
```
override def run(attemptId: Long): MapStatus = {
  val numOutputSplits = dep.partitioner.numPartitions
   
  ...
    // Partition the map output.
    val buckets = Array.fill(numOutputSplits)(new ArrayBuffer[(Any, Any)])
    for (elem <- rdd.iterator(split, taskContext)) {
      val pair = elem.asInstanceOf[(Any, Any)]
      val bucketId = dep.partitioner.getPartition(pair._1)
      buckets(bucketId) += pair
    }
    ...
    val blockManager = SparkEnv.get.blockManager
    for (i <- 0 until numOutputSplits) {
      val blockId = "shuffle_" + dep.shuffleId + "_" + partition + "_" + i
      // Get a Scala iterator from Java map
      val iter: Iterator[(Any, Any)] = buckets(i).iterator
      val size = blockManager.put(blockId, iter, StorageLevel.DISK_ONLY, false)
      totalBytes += size
    }
  ...
}
```
我已经将一些干扰代码删去。可以看到Spark在每一个Mapper中为每个Reducer创建一个bucket，并将RDD计算结果放进bucket中。需要注意的是**每个bucket是一个ArrayBuffer，也就是说Map的输出结果是会先存储在内存**。  
接着Spark会将ArrayBuffer中的Map输出结果写入block manager所管理的磁盘中，这里文件的命名方式为： shuffle_ + shuffle_id + "_" + map partition id + "_" + shuffle partition id。  
早期的shuffle write有两个比较大的问题：  
1. Map的输出必须先全部存储到内存中，然后写入磁盘。这对内存是一个非常大的开销，当内存不足以存储所有的Map output时就会出现OOM。  
2. 每一个Mapper都会产生Reducer number个shuffle文件，如果Mapper个数是1k，Reducer个数也是1k，那么就会产生1M个shuffle文件，这对于文件系统是一个非常大的负担。同时在shuffle数据量不大而shuffle文件又非常多的情况下，随机写也会严重降低IO的性能。  

在Spark 0.8版本中，shuffle write采用了与RDD block write不同的方式，同时也为shuffle write单独创建了ShuffleBlockManager，部分解决了0.6和0.7版本中遇到的问题。  
首先我们来看一下Spark 0.8的具体实现：  
```
override def run(attemptId: Long): MapStatus = {
  ...
  val blockManager = SparkEnv.get.blockManager
  var shuffle: ShuffleBlocks = null
  var buckets: ShuffleWriterGroup = null
  try {
    // Obtain all the block writers for shuffle blocks.
    val ser = SparkEnv.get.serializerManager.get(dep.serializerClass)
    shuffle = blockManager.shuffleBlockManager.forShuffle(dep.shuffleId, numOutputSplits, ser)
    buckets = shuffle.acquireWriters(partition)
    // Write the map output to its associated buckets.
    for (elem <- rdd.iterator(split, taskContext)) {
      val pair = elem.asInstanceOf[Product2[Any, Any]]
      val bucketId = dep.partitioner.getPartition(pair._1)
      buckets.writers(bucketId).write(pair)
    }
    // Commit the writes. Get the size of each bucket block (total block size).
    var totalBytes = 0L
    val compressedSizes: Array[Byte] = buckets.writers.map { writer:   BlockObjectWriter =>
      writer.commit()
      writer.close()
      val size = writer.size()
      totalBytes += size
      MapOutputTracker.compressSize(size)
    }
    ...
  } catch { case e: Exception =>
    // If there is an exception from running the task, revert the partial writes
    // and throw the exception upstream to Spark.
    if (buckets != null) {
      buckets.writers.foreach(_.revertPartialWrites())
    }
    throw e
  } finally {
    // Release the writers back to the shuffle block manager.
    if (shuffle != null && buckets != null) {
      shuffle.releaseWriters(buckets)
    }
    // Execute the callbacks on task completion.
    taskContext.executeOnCompleteCallbacks()
    }
  }
}
```
在这个版本中为shuffle write添加了一个新的类ShuffleBlockManager，由ShuffleBlockManager来分配和管理bucket。同时ShuffleBlockManager为每一个bucket分配一个DiskObjectWriter，每个write handler拥有默认100KB的缓存，使用这个write handler将Map output写入文件中。可以看到现在的写入方式变为buckets.writers(bucketId).write(pair)，也就是说Map output的key-value pair是逐个写入到磁盘而不是预先把所有数据存储在内存中再整体flush到磁盘中去。  

ShuffleBlockManager的代码如下所示：
```
private[spark]
class ShuffleBlockManager(blockManager: BlockManager) {
  def forShuffle(shuffleId: Int, numBuckets: Int, serializer: Serializer): ShuffleBlocks = {
    new ShuffleBlocks {
      // Get a group of writers for a map task.
      override def acquireWriters(mapId: Int): ShuffleWriterGroup = {
        val bufferSize = System.getProperty("spark.shuffle.file.buffer.kb", "100").toInt * 1024
        val writers = Array.tabulate[BlockObjectWriter](numBuckets) { bucketId =>
          val blockId = ShuffleBlockManager.blockId(shuffleId, bucketId, mapId)
          blockManager.getDiskBlockWriter(blockId, serializer, bufferSize)
        }
        new ShuffleWriterGroup(mapId, writers)
      }
      override def releaseWriters(group: ShuffleWriterGroup) = {
        // Nothing really to release here.
      }
    }
  }
}
```
Spark 0.8显著减少了shuffle的内存压力，现在Map output不需要先全部存储在内存中，再flush到硬盘，而是record-by-record写入到磁盘中。同时对于shuffle文件的管理也独立出新的ShuffleBlockManager进行管理，而不是与rdd cache文件在一起了。  

但是这一版Spark 0.8的shuffle write仍然有两个大的问题没有解决：  
- 首先依旧是shuffle文件过多的问题，shuffle文件过多一是会造成文件系统的压力过大，二是会降低IO的吞吐量。  
- 其次虽然Map output数据不再需要预先在内存中evaluate显著减少了内存压力，但是新引入的DiskObjectWriter所带来的buffer开销也是一个不容小视的内存开销。假定我们有1k个Mapper和1k个Reducer，那么就会有1M个bucket，于此同时就会有1M个write handler，而每一个write handler默认需要100KB内存，那么总共需要100GB的内存。这样的话仅仅是buffer就需要这么多的内存，内存的开销是惊人的。当然实际情况下这1k个Mapper是分时运行的话，所需的内存就只有cores * reducer numbers * 100KB大小了。但是reducer数量很多的话，这个buffer的内存开销也是蛮厉害的。  

为了解决shuffle文件过多的情况，Spark 0.8.1引入了新的shuffle consolidation，以期显著减少shuffle文件的数量。  
 
首先我们以图例来介绍一下shuffle consolidation的原理。  
![sparkShuffleConsolidate](http://jerryshao.me/img/2014-01-04-spark-shuffle/spark-shuffle-consolidate.png)  

### Reference  
- [spark使用总结](http://smallx.me/2016/06/07/spark%E4%BD%BF%E7%94%A8%E6%80%BB%E7%BB%93/)   
- [详细探究Spark的shuffle实现](http://jerryshao.me/architecture/2014/01/04/spark-shuffle-detail-investigation/)  

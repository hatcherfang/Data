### Transformation与Action  

RDD提供了两种类型的操作：transformation操作(转化操作)和action操作(行动操作)。transformation操作是得到一个新的RDD，方式很多，比如从数据源生成一个新的RDD，从RDD生成一个新的RDD。action操作则是得到其他数据类型的结果。  

所有的transformation都是采用的懒策略，就是如果只是将transformation提交是不会执行计算的，spark在内部只是用新的RDD记录这些transformation操作并形成RDD对象的有向无环图(DAG)，计算只有在action被提交的时候才被触发。实际上，我们不应该把RDD看作存放着特定数据的数据集，而最好把每个RDD当作我们通过transformation操作构建出来的、记录如何计算数据的**指令列表**。  

RDD的action算子会触发一个新的job，spark会在DAG中寻找是否有cached或者persisted的中间结果，如果没有找到，那么就会重新执行这些中间过程以重新计算该RDD。**因此，如果想在多个action操作中重用同一个RDD，那么最好使用 cache()/persist()将RDD缓存在内存中，但如果RDD过大，那么最好使用 persist(StorageLevel.MEMORY_AND_DISK) 代替**。**注意cache/persist仅仅是设置RDD的存储等级，因此你应该在第一次调用action之前调用cache/persist**。cache/persist使得中间计算结果存在内存中，这个才是说为啥Spark是内存计算引擎的地方。在MR里，你是要放到HDFS里的，但Spark允许你把中间结果放内存里。  

**在spark程序中打印日志时，尤其需要注意打印日志的代码很有可能使用到了action算子，如果没有缓存中间RDD就可能导致程序的效率大大降低。另外，如果一个RDD的计算过程中有抽样、随机值或者其他形式的变化，那么一定要缓存中间结果，否则程序执行结果可能都是不准确的！**  

### RDD的本质是什么  

一个RDD 本质上是一个函数，而RDD的变换不过是函数的嵌套。  
RDD我认为有两类：  
输入RDD,典型如KafkaRDD,JdbcRDD  
转换RDD，如MapPartitionsRDD  
我们以下面的代码为例做分析：  
```
sc.textFile("abc.log").map().saveAsTextFile("")
```
textFile 会构建出一个NewHadoopRDD,  
map函数运行后会构建出一个MapPartitionsRDD  
saveAsTextFile触发了实际流程代码的执行  

所以RDD不过是对一个函数的封装，当一个函数对数据处理完成后，我们就得到一个RDD的数据集(是一个虚拟的，后续会解释)。  

NewHadoopRDD是数据来源，每个parition负责获取数据，获得过程是通过iterator.next 获得一条一条记录的。假设某个时刻拿到了一条数据A,这个A会立刻被map里的函数处理得到B（完成了转换）,然后开始写入到HDFS上。其他数据重复如此。所以整个过程：  
- 理论上某个MapPartitionsRDD里实际在内存里的数据等于其Partition的数目，是个非常小的数值。  
- NewHadoopRDD则会略多些，因为属于数据源，读取文件，假设读取文件的buffer是1M，那么最多也就是partitionNum*1M 数据在内存里  
- saveAsTextFile也是一样的，往HDFS写文件，需要buffer，最多数据量为 buffer* partitionNum  
所以整个过程其实是流式的过程，一条数据被各个RDD所包裹的函数处理。  

刚才我反复提到了嵌套函数，怎么知道它是嵌套的呢？

如果你写了这样一个代码：
```
sc.textFile("abc.log").map().map().........map().saveAsTextFile("")
```
有成千上万个map,很可能就堆栈溢出了。为啥?实际上是函数嵌套太深了。

按上面的逻辑，内存使用其实是非常小的，10G内存跑100T数据也不是难事。但是为什么Spark常常因为内存问题挂掉呢？ 我们接着往下看。

### Shuffle的本质是什么？ 

这就是为什么要分Stage了。每个Stage其实就是我上面说的那样，一套数据被N个嵌套的函数处理(也就是你的transform动作)。遇到了Shuffle,就被切开来，所谓的Shuffle，本质上是把数据按规则临时都落到磁盘上，相当于完成了一个saveAsTextFile的动作，不过是存本地磁盘。然后被切开的下一个Stage则以本地磁盘的这些数据作为数据源，重新走上面描述的流程。  

我们再做一次描述：  

所谓Shuffle不过是把处理流程切分，给切分的上一段(我们称为Stage M)加个存储到磁盘的Action动作，把切分的下一段(Stage M+1)数据源变成Stage M存储的磁盘文件。每个Stage都可以走我上面的描述，让每条数据都可以被N个嵌套的函数处理，最后通过用户指定的动作进行存储。   

### 为什么Shuffle 容易导致Spark挂掉  

前面我们提到，Shuffle不过是偷偷的帮你加上了个类似saveAsLocalDiskFile的动作。然而，写磁盘是一个高昂的动作。所以我们尽可能的把数据先放到内存，再批量写到文件里，还有读磁盘文件也是个费内存的动作。把数据放内存，就遇到个问题，比如10000条数据，到底会占用多少内存？这个其实很难预估的。所以一不小心，就容易导致内存溢出了。这其实也是一个很无奈的事情。  

### 我们做Cache/Persist意味着什么？  

其实就是给某个Stage加上了一个saveAsMemoryBlockFile的动作，然后下次再要数据的时候，就不用算了。这些存在内存的数据就表示了某个RDD处理后的结果。这个才是说为啥Spark是内存计算引擎的地方。在MR里，你是要放到HDFS里的，但Spark允许你把中间结果放内存里。  

### 使用Spark Cache不仅仅为了性能考虑   
rdd在进行多次transformation操作之后对该RDD进行两次Action操作, 两次得到的RDD并不是通过transformation重新转换得来的，地址都不一样，如果想要实现相同就要使用cache或者persist来缓存RDD数据。  

### RDD持久化(缓存)  

正如在转化和行动操作部分所说的一样，为了避免在一个RDD上多次调用action操作从而可能导致的重新计算，我们应该将该RDD在第一次调用action之前进行持久化(rdd.setName("xxx").persist(StorageLevel.MEMORY_AND_DISK))。对RDD进行持久化对于迭代式和交互式应用非常有好处，好处大大滴有。  

持久化可以使用cache()或者persist()。默认情况下的缓存级别为MEMORY_ONLY，spark会将对象直接缓存在JVM的堆空间中，而不经过序列化处理。我们可以给persist()传递持久化级别参数以指定的方式持久化RDD。MEMORY_AND_DISK持久化级别尽量将RDD缓存在内存中，如果内存缓存不下了，就将剩余分区缓存在磁盘中。MEMORY_ONLY_SER将RDD进行序列化处理(每个分区序列化为一个字节数组)然后缓存在内存中。还有MEMORY_AND_DISK_SER等等很多选项。选择持久化级别的原则是：尽量选择缓存在内存中，如果内存不够，则首选序列化内存方式，除非RDD分区重算开销比缓存到磁盘来的更大(很多时候，重算RDD分区会比从磁盘中读取要快)或者序列化之后内存还是不够用，否则不推荐缓存到磁盘上。  

如果要缓存的数据太多，内存中放不下，spark会自动利用最近最少使用(LRU)策略把最老的分区从内存中移除。对于仅放在内存中的缓存级别，下次要用到已被移除的分区时，这些分区就需要重新计算。对于使用内存与磁盘的缓存级别，被移除的分区都会被写入磁盘。  

另外，RDD还有一个unpersist()方法，用于手动把持久化的RDD从缓存中移除。  

环境变量SPARK_LOCAL_DIRS用来设置RDD持久化到磁盘的目录，它同时也是shuffle的缓存目录。  

### Reference  
[spark使用总结](http://smallx.me/2016/06/07/spark%E4%BD%BF%E7%94%A8%E6%80%BB%E7%BB%93/)   
[Spark会把数据都载入到内存么？](http://www.jianshu.com/p/b70fe63a77a8)  
[Using Spark’s cache for correctness, not just performance](http://www.spark.tc/using-sparks-cache-for-correctness-not-just-performance/)  


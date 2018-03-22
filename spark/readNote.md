## 大数据处理流水线    
虽然MapReduce已经代表了一批应用程序，但这还不够，需要再进行抽象，提高一个层次，可以总结出**split-do-merge**模型。  
首先数据被分成若干部分，分割后的数据经过一组用户定义的函数来执行一些操作，从统计方法到机器学习，都可以。根据应用程序的数据处理需求，**do**操作可以不同，也可以组成一条操作链。最后结果会被用一种合并方法进行结合，如Reduce。  
上述一组大数据处理过程也称为大数据PipeLine，流水线。Pipe这个词最早出现在UNIX操作系统中，一个程序的输出作为另一个程序的输入。对大数据处理过程而言，在流水线中每一步的并行问题主要就是数据并行问题（data parallelism）。我们可以将数据并行简单地定义为对同一数据集的不同部分同时运行相同的函数。要达到这种数据并行，我们必须决定每步个并行计算的数据粒度，如WordCount中的Map的数据粒度是一行，shuffle and sort的数据粒度是单个键值对。你会发现每一步数据集的大小都减小了。  
## Reference  
[大数据处理流水线](http://blog.csdn.net/zhouweiyu/article/details/78982610)  
[Spark-1.6.0中的Sort Based Shuffle源码解读](http://blog.csdn.net/dabokele/article/details/51503001)  
[Spark中遇到的数据倾斜问题](https://www.jianshu.com/p/06b67a3c61a9)  
[Spark性能调优之道——解决Spark数据倾斜（Data Skew）的N种姿势](http://www.infoq.com/cn/articles/the-road-of-spark-performance-tuning)  

## RDD Base Convert   
1. map(func): 数据集中的每个元素经过用户自定义的函数转换形成一个新的RDD，新的RDD叫MappedRDD     
```
val rdd = sc.parallelize(1 to 10)  // create RDD 
val map = rdd.map(_*2)  // multiply 2 for each element
val map.collect()
```
```
output: 2 4 6 8 10 12 14 16 18 20
```
2. flatMap(func): 与map类似，但每个元素输入项都可以被映射到0个或多个的输出项，最终将结果"扁平化"后输出    
```
//...省略sc
   val rdd = sc.parallelize(1 to 5)
   val fm = rdd.flatMap(x => (1 to x)).collect()
```
```
output: 1 1 2 1 2 3 1 2 3 4 1 2 3 4 5
```
compared with map(func)  
```
//...省略sc
   val rdd = sc.parallelize(1 to 5)
   val fm = rdd.map(x => (1 to x)).collect()
```
```
output: Range(1) Range(1, 2) Range(1, 2, 3) Range(1, 2, 3, 4) Range(1, 2, 3, 4, 5)
```
3. mapPartitions(func):类似与map，map作用于每个分区的每个元素，但mapPartitions作用于每个分区  
func的类型：Iterator[T] => Iterator[U]  
假设有N个元素，有M个分区，那么map的函数的将被调用N次,而mapPartitions被调用M次,当在映射的过程中不断的创建对象时就可以使用mapPartitions比map的效率要高很多，比如当向数据库写入数据时，如果使用map就需要为每个元素创建connection对象，但使用mapPartitions的话就需要为每个分区创建connetcion对象  
输出有女性的名字：  
```
val l = List(("kpop","female"),("zorro","male"),("mobin","male"),("lucy","female"))
val rdd = sc.parallelize(l,2)
val mp = rdd.mapPartitions(x => x.filter(_._2 == "female")).map(x => x._1)　
```
```
output: kpop lucy
```
RDD依赖图  
4. mapPartitionsWithIndex(func):与mapPartitions类似，不同的时函数多了个分区索引的参数  
func类型：(Int, Iterator[T]) => Iterator[U]  
```
var rdd1 = sc.makeRDD(1 to 5,2)
//rdd1有两个分区
var rdd2 = rdd1.mapPartitionsWithIndex{
        (x,iter) => {
         var result = List[String]()
          var i = 0
	    while(iter.hasNext){
              i += iter.next()
            
	    }
         result.::(x + "|" + i).iterator
          }
}
//rdd2将rdd1中每个分区的数字累加，并在每个分区的累加结果前面加了分区索引
scala> rdd2.collect
res13: Array[String] = Array(0|3, 1|12)
```
5. sample(withReplacement,fraction,seed):以指定的随机种子随机抽样出数量为fraction的数据，withReplacement表示是抽出的数据是否放回，true为有放回的抽样，false为无放回的抽样  
eg: 从RDD中随机且有放回的抽出50%的数据，随机种子值为3（即可能以1 2 3的其中一个起始值）  
```
 val rdd = sc.parallelize(1 to 10)
 val sample1 = rdd.sample(true,0.5,3)
 sample1.collect.foreach(x => print(x + " "))
```
```
output: 2 3 4 5 6 7 8 10  
```
6. union(ortherDataset):将两个RDD中的数据集进行合并，最终返回两个RDD的并集，若RDD中存在相同的元素也不会去重  
```   
val rdd1 = sc.parallelize(1 to 3)
val rdd2 = sc.parallelize(3 to 5)
val unionRDD = rdd1.union(rdd2)
unionRDD.collect.foreach(x => print(x + " "))
```
```
output: 1 2 3 3 4 5
```
7. intersection(otherDataset):返回两个RDD的交集  
```
val rdd1 = sc.parallelize(1 to 3)
val rdd2 = sc.parallelize(3 to 5)
val unionRDD = rdd1.intersection(rdd2)
unionRDD.collect.foreach(x => print(x + " "))
```
```
output: 3
```
8. distinct([numTasks]):对RDD中的元素进行去重  
```
val list = List(1,1,2,5,2,9,6,1)
val distinctRDD = sc.parallelize(list)
val unionRDD = distinctRDD.distinct()
unionRDD.collect.foreach(x => print(x + " "))
```
```
output: 1 6 9 5 2
```
9. cartesian(otherDataset):对两个RDD中的所有元素进行笛卡尔积操作  
```
val rdd1 = sc.parallelize(1 to 3)
val rdd2 = sc.parallelize(2 to 5)
val cartesianRDD = rdd1.cartesian(rdd2)
cartesianRDD.foreach(x => println(x + " "))
```
```
output: 
(1,2)
(1,3)
(1,4)
(1,5)
(2,2)
(2,3)
(2,4)
(2,5)
(3,2)
(3,3)
(3,4)
(3,5)
```
10. coalesce(numPartitions，shuffle):对RDD的分区进行重新分区，shuffle默认值为false,当shuffle=false时，不能增加分区数  
目,但不会报错，只是分区个数还是原来的  
eg: shuffle=false  
```
val rdd = sc.parallelize(1 to 16,4)
val coalesceRDD = rdd.coalesce(3) //当suffle的值为false时，不能增加分区数(即分区数不能从5->7)
println("重新分区后的分区个数:"+coalesceRDD.partitions.size)　
```
```
output: 重新分区后的分区个数:3  
```
eg: shuffle=true 
```
val rdd = sc.parallelize(1 to 16,4)
val coalesceRDD = rdd.coalesce(7,true)
println("重新分区后的分区个数:"+coalesceRDD.partitions.size)
println("RDD依赖关系:"+coalesceRDD.toDebugString)
```
11. repartition(numPartition):是函数coalesce(numPartition,true)的实现，效果和例10.2的coalesce(numPartition,true)的一样  
12. glom():将RDD的每个分区中的类型为T的元素转换为数组Array[T]  
eg:  
```
val rdd = sc.parallelize(1 to 16,4)
val glomRDD = rdd.glom() //RDD[Array[T]]
glomRDD.collect()
```
```
output: res80: Array[Array[Int]] = Array(Array(1, 2, 3, 4), Array(5, 6, 7, 8), Array(9, 10, 11, 12), Array(13, 14, 15, 16))
```
RDD 依赖图略  
13. randomSplit(weight:Array[Double],seed):根据weight权重值将一个RDD划分成多个RDD,权重越高划分得到的元素较多的几率就越大  
```
//省略sc
val rdd = sc.parallelize(1 to 10)
val randomSplitRDD = rdd.randomSplit(Array(1.0,2.0,7.0))
randomSplitRDD(0).foreach(x => print(x +" "))
randomSplitRDD(1).foreach(x => print(x +" "))
randomSplitRDD(2).foreach(x => print(x +" "))
```
```
2 4
3 8 9
1 5 6 7 10
```
## RDD key-value transformation  
摘要：  
RDD：弹性分布式数据集，是一种特殊集合 ‚ 支持多种来源 ‚ 有容错机制 ‚ 可以被缓存 ‚ 支持并行操作，一个RDD代表一个分区里的数据集  
RDD有两种操作算子：  
   Transformation（转换）：Transformation属于延迟计算，当一个RDD转换成另一个RDD时并没有立即进行转换，仅仅是记住了数据集的逻辑操作  
   Ation（执行）：触发Spark作业的运行，真正触发转换算子的计算  
1.mapValus(fun):对[K,V]型数据中的V值map操作  
(例1)：对每个的的年龄加2  
```
val list = List(("mobin",22),("kpop",20),("lufei",23))
val rdd = sc.parallelize(list)
val mapValuesRDD = rdd.mapValues(_+2)
mapValuesRDD.foreach(println)
```
```
(mobin,24)
(kpop,22)
(lufei,25)
```
2. flatMapValues(fun)：对[K,V]型数据中的V值flatmap操作  
eg 2:  
```
val list = List(("mobin",22),("kpop",20),("lufei",23))
val rdd = sc.parallelize(list)
val mapValuesRDD = rdd.flatMapValues(x => Seq(x,"male"))
mapValuesRDD.foreach(println)
```
```
output: 
(mobin,22)
(mobin,male)
(kpop,20)
(kpop,male)
(lufei,23)
(lufei,male)
```
3.comineByKey(createCombiner,mergeValue,mergeCombiners,partitioner,mapSideCombine)  
  comineByKey(createCombiner,mergeValue,mergeCombiners,numPartitions)  
  comineByKey(createCombiner,mergeValue,mergeCombiners)  
createCombiner:在第一次遇到Key时创建组合器函数，将RDD数据集中的V类型值转换C类型值(V => C),  
eg:  
(x: Int) => (List(x), 1)  
   V            C   
mergeValue：合并值函数，再次遇到相同的Key时，将createCombiner道理的C类型值与这次传入的V类型值合并成一个C类型值（C,V）=>C,  
eg:  
(peo: (List[String], Int), x:String) => (List[String], Int)  
                C              V                C   
mergeCombiners:合并组合器函数，将C类型值两两合并成一个C类型值  
eg:  
(peo: (List[String], Int), x:String) => (List[String], Int)  
            C                 V                C     
partitioner：使用已有的或自定义的分区函数，默认是HashPartitioner  

mapSideCombine：是否在map端进行Combine操作,默认为true  
 
注意前三个函数的参数类型要对应；第一次遇到Key时调用createCombiner，再次遇到相同的Key时调用mergeValue合并值  
eg: 统计男性和女生的个数，并以（性别，（名字，名字....），个数）的形式输出  
```
val people = List(("male", "Mobin"), ("male", "Kpop"), ("female", "Lucy"), ("male", "Lufei"), ("female", "Amy"))
val rdd = sc.parallelize(people)
val combinByKeyRDD = rdd.combineByKey(
      (x: String) => (List(x), 1),
      (peo: (List[String], Int), x : String) => (x :: peo._1, peo._2 + 1),
      (sex1: (List[String], Int), sex2: (List[String], Int)) => (sex1._1 ::: sex2._1, sex1._2 + sex2._2)
)
combinByKeyRDD.foreach(println)
```
```
output:  
(male,(List(Lufei, Kpop, Mobin),3))
(female,(List(Amy, Lucy),2))
```
过程分解：  
```
Partition1:
K="male"  -->  ("male","Mobin")  --> createCombiner("Mobin") =>  peo1 = (  List("Mobin") , 1  )
K="male"  -->  ("male","Kpop")  --> mergeValue(peo1,"Kpop") =>  peo2 = (  "Kpop"  ::  peo1_1 , 1 + 1  )    //Key相同调用mergeValue函数对值进行合并
K="female"  -->  ("female","Lucy")  --> createCombiner("Lucy") =>  peo3 = (  List("Lucy") , 1  )
 
Partition2:
K="male"  -->  ("male","Lufei")  --> createCombiner("Lufei") =>  peo4 = (  List("Lufei") , 1  )
K="female"  -->  ("female","Amy")  --> createCombiner("Amy") =>  peo5 = (  List("Amy") , 1  )
 
Merger Partition:
K="male" --> mergeCombiners(peo2,peo4) => (List(Lufei,Kpop,Mobin))
K="female" --> mergeCombiners(peo3,peo5) => (List(Amy,Lucy))
```
(RDD依赖图)  
![RDD依赖图](http://images2015.cnblogs.com/blog/776259/201604/776259-20160412212449535-68303650.png)  
4.foldByKey(zeroValue)(func)  
  foldByKey(zeroValue,partitioner)(func)  
  foldByKey(zeroValue,numPartitiones)(func)  
foldByKey函数是通过调用CombineByKey函数实现的  
zeroVale：对V进行初始化，实际上是通过CombineByKey的createCombiner实现的  V =>  (zeroValue,V)，再通过func函数映射成新的值，即func(zeroValue,V),如例4可看作对每个V先进行  V=> 2 + V   
func: Value将通过func函数按Key值进行合并（实际上是通过CombineByKey的mergeValue，mergeCombiners函数实现的，只不过在这里，这两个函数是相同的）   
```
val people = List(("Mobin", 2), ("Mobin", 1), ("Lucy", 2), ("Amy", 1), ("Lucy", 3))
val rdd = sc.parallelize(people)
val foldByKeyRDD = rdd.foldByKey(2)(_+_)
foldByKeyRDD.foreach(println)
```
```
(Amy,3)
(Mobin,5)
(Lucy,7)
```
先对每个V都加2，再对相同Key的value值相加。  
5. reduceByKey(func,numPartitions):按Key进行分组，使用给定的func函数聚合value值, numPartitions设置分区数，提高作业并行度  
```
val arr = List(("A",3),("A",2),("B",1),("B",3))
val rdd = sc.parallelize(arr)
val reduceByKeyRDD = rdd.reduceByKey(_ +_)
reduceByKeyRDD.foreach(println)
```
```
output:
(A,5)
(A,4)
```
RDD依赖图  
![RDD依赖图](http://images2015.cnblogs.com/blog/776259/201604/776259-20160412212624160-794390988.png)  

6. groupByKey(numPartitions):按Key进行分组，返回[K,Iterable[V]]，numPartitions设置分区数，提高作业并行度  
```
val arr = List(("A",1),("B",2),("A",2),("B",3))
val rdd = sc.parallelize(arr)
val groupByKeyRDD = rdd.groupByKey()
groupByKeyRDD.foreach(println)
```
```
output:
(B,CompactBuffer(2, 3))
(A,CompactBuffer(1, 2))
```
7. sortByKey(accending，numPartitions):返回以Key排序的（K,V）键值对组成的RDD，accending为true时表示升序，为false时表示降序，numPartitions设置分区数，提高作业并行度  
```
val arr = List(("A",1),("B",2),("A",2),("B",3))
val rdd = sc.parallelize(arr)
val sortByKeyRDD = rdd.sortByKey()
sortByKeyRDD.foreach(println)
```
```
output:
(A,1)
(A,2)
(B,2)
(B,3)
```
8. cogroup(otherDataSet，numPartitions)：对两个RDD(如:(K,V)和(K,W))相同Key的元素先分别做聚合，最后返回(K,Iterator<V>,Iterator<W>)形式的RDD,numPartitions设置分区数，提高作业并行度  
```
val arr = List(("A", 1), ("B", 2), ("A", 2), ("B", 3))
val arr1 = List(("A", "A1"), ("B", "B1"), ("A", "A2"), ("B", "B2"))
val rdd1 = sc.parallelize(arr, 3)
val rdd2 = sc.parallelize(arr1, 3)
val groupByKeyRDD = rdd1.cogroup(rdd2)
groupByKeyRDD.foreach(println)
```
```
output:
(B,(CompactBuffer(2, 3),CompactBuffer(B1, B2)))
(A,(CompactBuffer(1, 2),CompactBuffer(A1, A2)))
```
RDD依赖图  
![RDD依赖图](http://images2015.cnblogs.com/blog/776259/201604/776259-20160412212738098-2084185268.png)  

9. join(otherDataSet,numPartitions):对两个RDD先进行cogroup操作形成新的RDD，再对每个Key下的元素进行笛卡尔积，numPartitions设置分区数，提高作业并行度  
eg:  
```
val arr = List(("A", 1), ("B", 2), ("A", 2), ("B", 3))
val arr1 = List(("A", "A1"), ("B", "B1"), ("A", "A2"), ("B", "B2"))
val rdd = sc.parallelize(arr, 3)
val rdd1 = sc.parallelize(arr1, 3)
val groupByKeyRDD = rdd.join(rdd1)
groupByKeyRDD.foreach(println)
```
```
output:  
(B,(2,B1))
(B,(2,B2))
(B,(3,B1))
(B,(3,B2))
 
(A,(1,A1))
(A,(1,A2))
(A,(2,A1))
(A,(2,A2))
```
10. leftOuterJoin(otherDataSet，numPartitions):左外连接，包含左RDD的所有数据，如果右边没有与之匹配的用None表示,numPartitions设置分区数，提高作业并行度  
```
val arr = List(("A", 1), ("B", 2), ("A", 2), ("B", 3),("C",1))
val arr1 = List(("A", "A1"), ("B", "B1"), ("A", "A2"), ("B", "B2"))
val rdd = sc.parallelize(arr, 3)
val rdd1 = sc.parallelize(arr1, 3)
val leftOutJoinRDD = rdd.leftOuterJoin(rdd1)
leftOutJoinRDD .foreach(println)
```
```
output:  

(B,(2,Some(B1)))
(B,(2,Some(B2)))
(B,(3,Some(B1)))
(B,(3,Some(B2)))
(C,(1,None))
(A,(1,Some(A1)))
(A,(1,Some(A2)))
(A,(2,Some(A1)))
(A,(2,Some(A2)))
```
11. rightOuterJoin(otherDataSet, numPartitions):右外连接，包含右RDD的所有数据，如果左边没有与之匹配的用None表示,numPartitions设置分区数，提高作业并行度  
```
val arr = List(("A", 1), ("B", 2), ("A", 2), ("B", 3))
val arr1 = List(("A", "A1"), ("B", "B1"), ("A", "A2"), ("B", "B2"),("C","C1"))
val rdd = sc.parallelize(arr, 3)
val rdd1 = sc.parallelize(arr1, 3)
val rightOutJoinRDD = rdd.rightOuterJoin(rdd1)
rightOutJoinRDD.foreach(println)
```
```
output: 

(B,(Some(2),B1))
(B,(Some(2),B2))
(B,(Some(3),B1))
(B,(Some(3),B2))
(C,(None,C1))
(A,(Some(1),A1))
(A,(Some(1),A2))
(A,(Some(2),A1))
(A,(Some(2),A2))
```
## RDD Action operation  
1. 1.reduce(func):通过函数func先聚集各分区的数据集，再聚集分区之间的数据，func接收两个参数，返回一个新值，新值再做为参数继续传递给函数func，直到最后一个元素  
eg:  
```
scala> val rdd = sc.parallelize(1 to 10)
rdd: org.apache.spark.rdd.RDD[Int] = ParallelCollectionRDD[131] at parallelize at <console>:24

scala> val reduceRDD = rdd.reduce(_+_)
reduceRDD: Int = 55
```
2. collect():以数据的形式返回数据集中的所有元素给Driver程序，为防止Driver程序内存溢出，一般要控制返回的数据集大小  
3. count()：返回数据集元素个数  
eg:  
```
scala> val rdd = sc.parallelize(1 to 10)
rdd: org.apache.spark.rdd.RDD[Int] = ParallelCollectionRDD[131] at parallelize at <console>:24

scala> rdd.count
res138: Long = 10
```
4. first():返回数据集的第一个元素  
eg:  
```
scala> val rdd = sc.parallelize(1 to 10)
rdd: org.apache.spark.rdd.RDD[Int] = ParallelCollectionRDD[131] at parallelize at <console>:24

scala> rdd.first()
res140: Int = 1
```
5. take(n):以数组的形式返回数据集上的前n个元素  
eg:  
```
scala> val rdd = sc.parallelize(1 to 10)
rdd: org.apache.spark.rdd.RDD[Int] = ParallelCollectionRDD[131] at parallelize at <console>:24

scala> rdd.take(3)
res141: Array[Int] = Array(1, 2, 3)
```
6. top(n):按默认或者指定的排序规则返回前n个元素，默认按降序输出  
```
scala> val rdd = sc.parallelize(1 to 10)
rdd: org.apache.spark.rdd.RDD[Int] = ParallelCollectionRDD[131] at parallelize at <console>:24

scala> rdd.top(3)
res142: Array[Int] = Array(10, 9, 8)
```
7. takeOrdered(n,[ordering]): 按自然顺序或者指定的排序规则返回前n个元素  
```
scala> val rdd = sc.parallelize(1 to 10)
rdd: org.apache.spark.rdd.RDD[Int] = ParallelCollectionRDD[131] at parallelize at <console>:24

scala> rdd.takeOrdered(3) //按自然顺序从底到高输出前三个元素
res143: Array[Int] = Array(1, 2, 3)
```
(RDD依赖图：红色块表示一个RDD区，黑色块表示该分区集合，下同)  
![reduce RDD 依赖图](http://images2015.cnblogs.com/blog/776259/201604/776259-20160420211125679-465741576.png)  

8. countByKey():作用于K-V类型的RDD上，统计每个key的个数，返回(K,K的个数)  
```
val arr = List(("A", 1), ("B", 2), ("A", 2), ("B", 3), ("C", 4))
val rdd = sc.parallelize(arr,2)
val countByKeyRDD = rdd.countByKey()
countByKeyRDD.foreach(println)
```
```
output:

(B,2)
(A,2)
(C,1)
```
9. collectAsMap():作用于K-V类型的RDD上，作用与collect不同的是collectAsMap函数不包含重复的key，对于重复的key。后面的元素覆盖前面的元素  
```
val arr = List(("A", 1), ("B", 2), ("A", 2), ("B", 3), ("C", 4))
val rdd = sc.parallelize(arr,2)
val collectAsMapRDD = rdd.collectAsMap()
countByKeyRDD.foreach(println)
```
```
output:

(A,2)
(C,4)
(B,3)
```
10. lookup(k)：作用于K-V类型的RDD上，返回指定K的所有V值  
```
val arr = List(("A", 1), ("B", 2), ("A", 2), ("B", 3), ("C", 4))
val rdd = sc.parallelize(arr,2)
val lookupRDD = rdd.lookup("A")
lookupRDD.foreach(println)
```
```
1
2
```
RDD依赖图  
![lookupRDD依赖图](http://images2015.cnblogs.com/blog/776259/201604/776259-20160420211321898-953494488.png)  

11. aggregate(zeroValue:U)(seqOp:(U,T) => U,comOp(U,U) => U):  
seqOp函数将每个分区的数据聚合成类型为U的值，comOp函数将各分区的U类型数据聚合起来得到类型为U的值  
```
val rdd = sc.parallelize(List(1,2,3,4),2)
val aggregateRDD = rdd.aggregate(2)(_+_,_ * _)
println(aggregateRDD)
```
```
output:  
90
```
步骤1：分区1：zeroValue+1+2=5   分区2：zeroValue+3+4=9  
 
步骤2：zeroValue*分区1的结果*分区2的结果=90  

RDD依赖图  
![RDD依赖图](http://images2015.cnblogs.com/blog/776259/201604/776259-20160420211348273-88463613.png)  

12. fold(zeroValue:T)(op:(T,T) => T):通过op函数聚合各分区中的元素及合并各分区的元素，op函数需要两个参数，在开始时第一个传入的参数为zeroValue,T为RDD数据集的数据类型，，其作用相当于SeqOp和comOp函数都相同的aggregate函数  
```
val rdd = sc.parallelize(Array(("a", 1), ("b", 2), ("a", 2), ("c", 5), ("a", 3)), 2)
val foldRDD = rdd.fold(("d", 0))((val1, val2) => { if (val1._2 >= val2._2) val1 else val2})
println(foldRDD)
```
```
output:
c,5
```
其过程如下：  
```
1.开始时将(“d”,0)作为op函数的第一个参数传入，将Array中和第一个元素("a",1)作为op函数的第二个参数传入，并比较value的值，返回value值较大的元素  
 
2.将上一步返回的元素又作为op函数的第一个参数传入，Array的下一个元素作为op函数的第二个参数传入，比较大小  
 
3.重复第2步骤  
 
每个分区的数据集都会经过以上三步后汇聚后再重复以上三步得出最大值的那个元素，对于其他op函数也类似，只不过函数里的处理数据的方式不同而已  
```

RDD依赖图  
![RDD依赖图](http://images2015.cnblogs.com/blog/776259/201604/776259-20160420211420335-1384986861.png)  

13. saveAsFile(path:String):将最终的结果数据保存到指定的HDFS目录中(can not find)  
14. saveAsSequenceFile(path:String):将最终的结果数据以sequence的格式保存到指定的HDFS目录中(can not find)  


### parallelize  
## Reference:  
1. [Spark函数详解系列之RDD基本转换](http://www.cnblogs.com/MOBIN/p/5373256.html#5)  
2. [Spark常用函数讲解之键值RDD转换](http://www.cnblogs.com/MOBIN/p/5384543.html)  
3. [Spark常用函数讲解之Action操作](http://www.cnblogs.com/MOBIN/p/5414490.html)  

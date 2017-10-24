## [Best Practices](https://databricks.gitbooks.io/databricks-spark-knowledge-base/content/best_practices/README.html)  
### [Avoid GroupByKey](https://databricks.gitbooks.io/databricks-spark-knowledge-base/content/best_practices/prefer_reducebykey_over_groupbykey.html)  
try to replace GroupByKey with reduceByKey.  
`reduceBykey`: pairs on the same machine with the same key are combined(by using the lambda function passed into reduceByKey) before the data is shuffled. Then the lambda function is called again to reduce all the values from each partition to produce one final result.  
`groupByKey`: On the other hand, when calling groupByKey - all the key-value pairs are shuffled around. This is a lot of unnessary data to being transferred over the network.  

### [Don not copy all elements of a large RDD to the driver](https://databricks.gitbooks.io/databricks-spark-knowledge-base/content/best_practices/dont_call_collect_on_a_very_large_rdd.html)  
If your RDD is so large that all of it's elements won't fit in memory on the drive machine, don not do this.  
```
val values = myVeryLargeRDD.collect()
```
Collect will attempt to copy every single element in the RDD onto the single driver program, and then run out of memory and crash.  

Instead, you can make sure the number of elements you return is capped by calling take or takeSample, or perhaps filtering or sampling your RDD.  

Similarly, be cautious of these other actions as well unless you are sure your dataset size is small enough to fit in memory:  

- countByKey  
- countByValue  
- collectAsMap  

If you really do need every one of these values of the RDD and the data is too big to fit into memory, you can write out the RDD to files or export the RDD to a database that is large enough to hold all the data.  

### [Gracefully Dealing with Bad Input Data](https://databricks.gitbooks.io/databricks-spark-knowledge-base/content/best_practices/dealing_with_bad_data.html)  
When dealing with vast amounts of data, a common problem is that a small amount of the data is malformed or corrupt. Using a filter transformation, you can easily discard bad inputs, or use a map transformation if it's possible to fix the bad input. Or perhaps the best option is to use a flatMap function where you can try fixing the input but fall back to discarding the input if you can't.  
## [General Troubleshooting](https://databricks.gitbooks.io/databricks-spark-knowledge-base/content/troubleshooting/README.html)  
### [Job aborted due to stage failure: Task not serializable](https://databricks.gitbooks.io/databricks-spark-knowledge-base/content/troubleshooting/javaionotserializableexception.html)  
If you see this error:  
```
org.apache.spark.SparkException: Job aborted due to stage failure: Task not serializable: java.io.NotSerializableException: ...  
```
The above error can be triggered when you intialize a variable on the driver (master), but then try to use it on one of the workers. In that case, Spark Streaming will try to serialize the object to send it over to the worker, and fail if the object is not serializable. Consider the following code snippet:  
```
NotSerializable notSerializable = new NotSerializable();
JavaRDD<String> rdd = sc.textFile("/tmp/myfile");

rdd.map(s -> notSerializable.doSomething(s)).collect();
```
This will trigger that error. Here are some ideas to fix this error:  
- Serializable the class  
- Declare the instance only within the lambda function passed in map.  
- Make the NotSerializable object as a static and create it once per machine.  
- Call rdd.forEachPartition and create the NotSerializable object in there like this:  
```
rdd.forEachPartition(iter -> {
  NotSerializable notSerializable = new NotSerializable();

  // ...Now process iter

		});
```
### [Missing Dependencies in Jar Files](https://databricks.gitbooks.io/databricks-spark-knowledge-base/content/troubleshooting/missing_dependencies_in_jar_files.html)  
### [Error running start-all.sh Connection refused]()  
If you are on a Mac and run into the following error when running start-all.sh:  

```
% sh start-all.sh
starting org.apache.spark.deploy.master.Master, logging to ...
localhost: ssh: connect to host localhost port 22: Connection refused
```
You need to enable "Remote Login" for your machine. From System Preferences, select Sharing, and then turn on Remote Login.  
### [Network connectivity issues between Spark components](https://databricks.gitbooks.io/databricks-spark-knowledge-base/content/troubleshooting/connectivity_issues.html)  

## [Performance & Optimization](https://databricks.gitbooks.io/databricks-spark-knowledge-base/content/performance_optimization/README.html)  
### [How Many Partitions Does An RDD Have?](https://databricks.gitbooks.io/databricks-spark-knowledge-base/content/performance_optimization/how_many_partitions_does_an_rdd_have.html)  
### [Data Locality](https://databricks.gitbooks.io/databricks-spark-knowledge-base/content/performance_optimization/data_locality.html)  

## [Spark Streaming](https://databricks.gitbooks.io/databricks-spark-knowledge-base/content/spark_streaming/README.html)  
### [ERROR OneForOneStrategy](https://databricks.gitbooks.io/databricks-spark-knowledge-base/content/spark_streaming/error_oneforonestrategy.html)  

### reference:  
[Databricks Spark Knowledge Base](https://www.gitbook.com/book/databricks/databricks-spark-knowledge-base/details)  

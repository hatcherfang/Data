### DataFrame  
```
scala> val dataset = Seq((0, "hello"), (1, "world")).toDF("id", "text")
scala> val upper: String => String = _.toUpperCase
upper: String => String = <function1>

scala> import org.apache.spark.sql.functions.udf
import org.apache.spark.sql.functions.udf

scala> val upperUDF = udf(upper)
upperUDF: org.apache.spark.sql.expressions.UserDefinedFunction = UserDefinedFunction(<function1>,StringType,Some(List(StringType)))

scala> dataset.withColumn("uppper", upperUDF('text)).show
+---+-----+------+
| id| text|uppper|
+---+-----+------+
|  0|hello| HELLO|
|  1|world| WORLD|
+---+-----+------+
'))

scala> dataset.createOrReplaceTempView("T1")

scala> val sqlDF = spark.sql("select * from T1")
sqlDF: org.apache.spark.sql.DataFrame = [id: int, text: string]

scala> sqlDF.show()
+---+-----+
| id| text|
+---+-----+
|  0|hello|
|  1|world|
+---+-----+

scala> val sqlDF_id = spark.sql("select id from T1")
sqlDF_id: org.apache.spark.sql.DataFrame = [id: int]

scala> sqlDF_id.show()
+---+
| id|
+---+
|  0|
|  1|
+---+
```

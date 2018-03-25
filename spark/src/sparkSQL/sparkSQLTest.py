# A simple demo for working with SparkSQL
'''
spark-submit sparkSQLTest.py testweets.json
'''
from pyspark import SparkContext, SparkConf
from pyspark.sql import SQLContext, Row
from pyspark.sql.types import IntegerType
from pyspark.sql.functions import udf
import sys
import time

def convertUpper(x):
    return x.upper()

if __name__ == "__main__":
    # read json file
    inputFile = sys.argv[1]
    conf = SparkConf().setAppName("SparkSQLTwitter")
    sc = SparkContext(conf=conf)
    sqlCtx = SQLContext(sc)
    input = sqlCtx.read.json(inputFile)
    # print data schema
    # print input.printSchema()
    # get partitions number
    print input.rdd.getNumPartitions()
    input.createOrReplaceTempView("tb_data")
    sqlCtx.cacheTable("tb_data")
    data = sqlCtx.sql("select * from tb_data")
    print "----read json file and save as parquet file----"
    data.show()
    data.write.save("./parquetFile", mode="overwrite", format="parquet")
    # Read parquet file
    print "----read parquet file and show----"
    rows = sqlCtx.read.parquet("./parquetFile")
    print rows.show()
    # Use Row to create DataFrame base on RDD
    happyPeopleRDD = sc.parallelize([Row(name="holden", favouriteBeverage="coffee")])
    happyPeopleSchemaRDD = sqlCtx.createDataFrame(happyPeopleRDD)
    happyPeopleSchemaRDD.createOrReplaceTempView("happy_people")
    print sqlCtx.sql("select * from happy_people").show()
    # UDF
    funUDF = udf(lambda x: convertUpper(x))
    dataSet = sc.parallelize([Row(id="1", text="hello"), Row(id="2", text="world")])
    dataSetDataFrame = sqlCtx.createDataFrame(dataSet)
    dataSetDataFrame.createOrReplaceTempView("udfTest")
    dataSetDataFrame.show()
    dataSetDataFrame.withColumn("text", funUDF(dataSetDataFrame.text)).show()
    dataSetDataFrame.withColumn("UPPER_TEXT", funUDF("text")).show()
    sqlCtx.registerFunction("Upper", lambda x: convertUpper(x))
    convertUpperRDD = sqlCtx.sql("select Upper(text) from udfTest")
    convertUpperRDD.show()
    
    time.sleep(10000)

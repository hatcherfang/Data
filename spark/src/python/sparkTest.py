# -*- coding: UTF-8 -*-
import sys
import time

from pyspark import SparkContext

class SearchFunctions(object):
    def __init__(self, query):
        self.query = query

    def isMatch(self, s):
        return self.query in s

    def getMatchesFunctionReference(self, rdd):
        # problem: "self.isMatch", self is refered
        return rdd.filter(self.isMatch)

    def getMatchesMemberReference(self, rdd):
        # problem: "self.query", self is refered
        # solution: replace self member with local variable
        query = self.query
        return rdd.filter(lambda x: query in x)

def test0315():
    master = "local"
    if len(sys.argv) == 2:
        master = sys.argv[1]
    sc = SparkContext(master, "03_19test")
    rdd = sc.parallelize(["pandas", "i like pandas", "hatcher"])
    sf = SearchFunctions("pandas")
    rddFilter = sf.getMatchesFunctionReference(rdd)
    print rddFilter.collect()
    rddFilter2 = sf.getMatchesMemberReference(rdd)
    print rddFilter2.collect()

def test0326():
    master = "local"
    if len(sys.argv) == 2:
        master = sys.argv[1]
    sc = SparkContext(master, "03_26test")
    numsRDD = sc.parallelize([1, 2, 3, 4])
    squared = numsRDD.map(lambda x: x*x).collect()
    for num in squared:
        print num

def test0329():
    master = "local"
    if len(sys.argv) == 2:
        master = sys.argv[1]
    sc = SparkContext(master, "03_29test")
    lines = sc.parallelize(["hatcher fang", "a b c"])
    flatMapRDD = lines.flatMap(lambda line: line.split(" "))
    print flatMapRDD.collect()

def add(x, y):
    return x+y

def test0332():
    master = "local"
    if len(sys.argv) == 2:
        master = sys.argv[1]
    sc = SparkContext(master, "03_32test")
    rdd = sc.parallelize([1, 2, 3, 4])
    print rdd.reduce(lambda x, y: x+y)
    print rdd.fold(0, add)
    sumCount = rdd.aggregate((0, 0), 
                   (lambda acc, value: (acc[0] + value, acc[1] + 1)),
                   (lambda acc1, acc2: (acc1[0] + acc2[0], acc1[1] + acc2[1])))
    average = sumCount[0]/float(sumCount[1])
    print sumCount, average

def test0401():
    master = "local"
    if len(sys.argv) == 2:
        master = sys.argv[1]
    sc = SparkContext(master, "04_01test")
    lines = sc.textFile("./sparkTest.scala")
    pairs = lines.map(lambda x: (x.split(" ")[0], x))
    print pairs.collect()

def testTable4_1():
    master = "local"
    if len(sys.argv) == 2:
        master = sys.argv[1]
    sc = SparkContext(master, "4_1table")
    rdd = sc.parallelize(((1, 2), (3, 4), (3, 6)))
    print rdd.collect()
    reduceByKeyRdd = rdd.reduceByKey(lambda x, y: x+y)
    print "reduceByKeyRdd:"
    print reduceByKeyRdd.collect()

    groupByKeyRdd = rdd.groupByKey()
    print "groupByKeyRdd:"
    print groupByKeyRdd.collect()

    mapValuesRdd = rdd.mapValues(lambda x: x+1)
    print "mapValuesRdd:"
    print mapValuesRdd.collect()

    flatMapValuesRdd = rdd.flatMapValues(lambda x: [x for x in range(5)])
    print "flatMapValuesRdd:"
    print flatMapValuesRdd.collect()

    keysRdd = rdd.keys()
    print "keysRdd:"
    print keysRdd.collect()

    valuesRdd = rdd.values()
    print "valuesRdd:"
    print valuesRdd.collect()

    sortByKeyRdd = rdd.sortByKey()
    print "sortByKeyRdd:"
    print sortByKeyRdd.collect()

def testTable4_2():
    master = "local"
    if len(sys.argv) == 2:
        master = sys.argv[1]
    sc = SparkContext(master, "4_2table")
    rdd = sc.parallelize([(1, 2), (3, 4), (3, 6)])
    other = sc.parallelize([(3, 9)])
    print "rdd:%r, other:%r" % (rdd.collect(), other.collect())
    print "subtractByKey:"
    print rdd.subtractByKey(other).collect()
    print "join:"
    print rdd.join(other).collect()
    print "rightOuterJoin:"
    print rdd.rightOuterJoin(other).collect()
    print "leftOuterJoin:"
    print rdd.leftOuterJoin(other).collect()
    print "cogroup:"
    print rdd.cogroup(other).collect()

def test4_7():
    master = "local"
    if len(sys.argv) == 2:
        master = sys.argv[1]
    sc = SparkContext(master, "4_7test")
    rdd = sc.parallelize([(1, 2), (3, 4), (3, 6)])
    print rdd.mapValues(lambda x: (x, 1)).collect()
    print rdd.mapValues(lambda x: (x, 1)).reduceByKey(lambda x, y: (x[0] + y[0], x[1] + y[1])).collect()

def test4_9():
    # word count
    master = "local"
    if len(sys.argv) == 2:
        master = sys.argv[1]
    sc = SparkContext(master, "test")
    rdd = sc.textFile("./sparkTest.scala")
    words = rdd.flatMap(lambda x: x.split(" "))
    print "words split:"
    print words.collect()
    result = words.map(lambda x: (x, 1)).reduceByKey(lambda x, y: x + y)
    print "words map and reduceByKey:"
    print result.collect()
    # method 2
    print "method 2, countByValue:"
    result = words.countByValue()
    print result
    print result["import"]

def test4_12():
    # use combineByKey() to calculate the average value for each key
    master = "local"
    if len(sys.argv) == 2:
        master = sys.argv[1]
    sc = SparkContext(master, "test")
    # list1 = [("male", "Mobin"), ("male", "Kpop"), ("female", "Lucy"), ("male", "Lufei"), ("female", "Amy")]
    list1 = [("A", 0), ("B", 1), ("C", 3), ("B", 3), ("A", 1), ("A", 2), ("A", 3), ("A", 5), ("A", 6)]
    ts1 = time.time()
    # rdd = sc.parallelize(list1, 2)
    rdd = sc.parallelize(list1)
    print "partition numbers:%d" % rdd.getNumPartitions()
    # rdd = sc.textFile("./sparkTest.scala")
    # print rdd.collect()
    # combineByKey(createCombiner, mergeValue, mergeCombiners)
    sumCount = rdd.combineByKey((lambda x: (x, 1)),
                                (lambda x, y:(x[0] + y, x[1] + 1)),
                                (lambda x, y:(x[0] + y[0], x[1] + y[1])))
    print sumCount.collect()
    print sumCount.map(lambda (key, xy): (key, xy[0]/float(xy[1]))).collectAsMap()
    print time.time()-ts1

def test4_15():
    # 例 4-15：在 Python 中自定义 reduceByKey() 的并行度 
    master = "local"
    if len(sys.argv) == 2:
        master = sys.argv[1]
    sc = SparkContext(master, "test")
    data = [("a", 3), ("b", 4), ("a", 1)] 
    ts = time.time()
    print sc.parallelize(data).reduceByKey(lambda x, y: x + y).collect()      # 默认并行度 
    print time.time()-ts
    # reduceByKey 第二个参数用来指定分组结果或聚合结果的RDD的分区数
    sc.parallelize(data).reduceByKey(lambda x, y: x + y, 100)  # 自定义并行度
    print time.time()-ts

def test4_19():
    # 在python中以字符串顺序对整数进行自定义排序
    master = "local"
    if len(sys.argv) == 2:
        master = sys.argv[1]
    sc = SparkContext(master, "test")
    data = [(124, "one"), (23, "two"), (32, "three")]
    rdd = sc.parallelize(data)
    print rdd.sortByKey(ascending=True, numPartitions=None, keyfunc = lambda x: str(x)).collect()

def testPairRDD_Action():
    # pair RDD的行动操作
    # countByKey() 对每个键对应的元素分别计数
    # collectAsMap() 将结果以映射表的形式返回，以便查询
    # lookup(key) 返回给定键对应的所有值
    master = "local"
    if len(sys.argv) == 2:
        master = sys.argv[1]
    sc = SparkContext(master, "test")
    data = [(1, 2), (3, 4), (3, 6)]
    rdd = sc.parallelize(data)
    print rdd.collect()
    print rdd.countByKey()
    print rdd.collectAsMap()
    print rdd.lookup(3)


def test5_1():
    # 在python中读取一个文本文件
    master = "local"
    if len(sys.argv) == 2:
        master = sys.argv[1]
    sc = SparkContext(master, "test")
    # inputFile = sc.textFile("file:///home/app/spark/spark-2.2.0-bin-hadoop2.7/README.md")
    # print '\n'.join(inputFile.collect())
    # 读取指定目录下的所有文件
    inputDirectory = sc.wholeTextFiles("file:///home/app/spark/spark-2.2.0-bin-hadoop2.7/hatchercode")
    print inputDirectory.collect()
    print inputDirectory.keys().collect()

def test5_5():
    # 在python中保存为文本文件
    master = "local"
    if len(sys.argv) == 2:
        master = sys.argv[1]
    sc = SparkContext(master, "test")
    inputFile = sc.textFile("file:///home/app/spark/spark-2.2.0-bin-hadoop2.7/README.md").repartition(4)
    inputFile.saveAsTextFile("file:///home/app/spark/spark-2.2.0-bin-hadoop2.7/README.md.output")

def test5_6():
    # 在python中读取非结构化的JSON
    import json
    master = "local"
    if len(sys.argv) == 2:
        master = sys.argv[1]
    sc = SparkContext(master, "test")
    inputJson = sc.textFile("./learning-spark/files/pandainfo.json")
    data = inputJson.map(lambda x: json.loads(x))
    # print data.collect()
    # attention: not use x['lovesPandas'] or there will be error when the key not exists
    lovesPandasRdd = data.filter(lambda x: x.get("lovesPandas"))
    lovesPandasRdd.saveAsTextFile("jsonOutput")

def test5_7():
    # 在python中读取CSV
    import csv
    import StringIO
    master = "local"
    if len(sys.argv) == 2:
        master = sys.argv[1]
    sc = SparkContext(master, "test")
    # refer  learning-spark/src/python/LoadCsv.py

def test5_20():
    # 在python中读取SequenceFile
    master = "local"
    if len(sys.argv) == 2:
        master = sys.argv[1]
    sc = SparkContext(master, "test")
    # create sequenceFile 
    data = sc.parallelize([("Panda", 3), ("Kay", 6), ("Snail", 2)])
    # data.saveAsSequenceFile("sequenceOutput")
    # data = sc.sequenceFile("./sequenceOutput", "org.apache.hadoop.io.Text", "org.apache.hadoop.io.IntWritable")
    print data.collect()


if __name__ == "__main__":
    # test0315()
    # test0326()
    # test0329()
    # test0332()
    # test0401()
    # testTable4_1()
    # testTable4_2()
    # test4_7()
    # test4_9()
    # test4_12()
    # test4_15()
    # test4_19()
    # testPairRDD_Action()
    # test5_1()
    # test5_5()
    # test5_6()
    test5_20()

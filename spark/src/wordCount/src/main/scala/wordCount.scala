/**
 * 功能：用spark实现的单词计数程序
 */

// 导入相关类库
import org.apache.spark._

object WordCount {
  def main(args: Array[String]) {
    // 建立spark运行上下文
    val sc = new SparkContext("local[*]", "WordCount", new SparkConf())

    // 加载数据，创建RDD
    val inRDD = sc.textFile("/root/report_log.access.1144.20171110", 3)

    // 对RDD进行转换，得到最终结果
    val res = inRDD.flatMap(_.split('\t')).map((_, 1)).reduceByKey(_ + _)

    // 将计算结果collect到driver节点，并打印
    res.collect.foreach(println)

    // 停止spark运行上下文
    // sc.stop()
  }
}

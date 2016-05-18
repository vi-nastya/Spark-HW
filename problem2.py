#!/usr/bin/env python
import re
import sys
from pyspark import SparkContext
from pyspark import SparkConf
from pyspark.sql import SQLContext
from pyspark.sql import Row, StructField, StructType, StringType, IntegerType
from datetime import datetime as dt


# regular expression for parsing log lines
log_format = re.compile(
    r"(?P<host>[\d\.]+)\s"
    r"(?P<identity>\S*)\s"
    r"(?P<user>\S*)\s"
    r"\[(?P<time>.*?)\]\s"
    r'"(?P<request>.*?)"\s'
    r"(?P<status>\d+)\s"
    r"(?P<bytes>\S*)\s"
    r'"(?P<referer>.*?)"\s'
    r'"(?P<user_agent>.*?)"\s*'
)

# Parse log line, return tuple with typed values
def parseLine(line):
    match = log_format.match(line)
    if not match:
        return ("", "", "", "", "", "", "" ,"")

    request = match.group('request').split()
    return (match.group('host'), match.group('time').split()[0], \
       request[0], request[1], match.group('status'), match.group('bytes'), \
        match.group('referer'), match.group('user_agent'),
        dt.strptime(match.group('time').split()[0], '%d/%b/%Y:%H:%M:%S').hour)

#Напишите программу, выводящую на экран суммарное количество переданной информации для каждого клиента. 

if __name__ == "__main__":
    conf = SparkConf().setAppName("vinastya_2_spark_app").setMaster(sys.argv[1]).set("spark.ui.port", "4090")
    sc = SparkContext(conf=conf)
    lines = sc.textFile("%s" % sys.argv[2])
    objects = lines.map(parseLine)

    #use "bytes" as value instead of 1s
    cnt_bytes_by_ip = objects.map(lambda line_tuple: (line_tuple[0], int(line_tuple[-4]))) \
                    .reduceByKey(lambda a, b: a + b) \
                    .map(lambda (a,b): (b,a) ) \
                    .sortByKey(False) \
		    .cache()


    vals = cnt_bytes_by_ip.collect()
    for val in vals:
        print('%s %s' % (val[0], val[1]))
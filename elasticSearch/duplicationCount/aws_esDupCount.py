import logging
import traceback
import collections
import requests
from requests_aws4auth import AWS4Auth
from setting import m_Body
from setting import timeStart, timeEnd, timeInterval
from setting import ES_AKEY, ES_SKEY, es_host, es_region, es_index
import json
import gevent
from gevent import monkey
monkey.patch_all()
statisticalDict = collections.defaultdict(list)


logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s %(filename)s(line:%(lineno)d) %(levelname)s] %(message)s',
    datefmt='%a, %d %b %Y %H:%M:%S',
    filename='myapp_aws_esDupCount.log',
    filemode='ab+')


def queryDuplicate(awsauth, endpoint, body, timeStart, timeEnd):
    try:
        logging.debug("timeStart:%r, timeEnd:%r", timeStart, timeEnd)
        body["query"]["bool"]["filter"][0]["range"]["CLF_UTCTimeStamp"]["gte"]\
            = timeStart
        body["query"]["bool"]["filter"][0]["range"]["CLF_UTCTimeStamp"]["lt"]\
            = timeEnd
        schema = json.dumps(body)
        response = {}
        response = requests.get(endpoint, data=schema, auth=awsauth)
        response = response.json()
        logging.debug(json.dumps(response, indent=4))
        buckets = response["aggregations"]["duplicate_count"]["buckets"]
        for bucket in buckets:
            dupList = bucket["duplicate_log"]["buckets"]
            for dupDic in dupList:
                if bucket["key"] not in statisticalDict:
                    statisticalDict[bucket["key"]] = [[dupDic["key"],
                                                      dupDic["doc_count"],
                                                      timeStart, timeEnd]]
                else:
                    statisticalDict[bucket["key"]].append([dupDic["key"],
                                                           dupDic["doc_count"],
                                                           timeStart, timeEnd])

        # print json.dumps(body, indent=4)
        # print '-------------------------------------------------'
    except:
        logging.error("response:%r, traceback:%r, timeStart:%r, timeEnd:%r",
                      response, traceback.print_exc(), timeStart, timeEnd)


def statisticalDup(statisticalDict):
    try:
        global dupCount
        for key, srcFileList in statisticalDict.iteritems():
            keyDupCount = {}
            total = 0
            for srcFile in srcFileList:
                dicKey = str(srcFile[0]) + '_' + str(key)
                if dicKey not in keyDupCount:
                    keyDupCount[dicKey] = srcFile[1] - 1
                else:
                    keyDupCount[dicKey] = keyDupCount[dicKey] + srcFile[1] - 1
                logging.info("srcFile_CLF_ID:%r, dupCount:%r",
                             dicKey, keyDupCount[dicKey])
                dupCount = dupCount + keyDupCount[dicKey]
                total = total + keyDupCount[dicKey]
            logging.info("srcFile:%r, duplication total:%r", key, total)
    except:
        logging.error("traceback:%r", traceback.print_exc())


if __name__ == "__main__":
    awsauth = AWS4Auth(ES_AKEY, ES_SKEY, es_region, 'es')
    endpoint = 'https://' + es_host + \
        '/' + es_index + '/iws-rawlog1/_search?pretty'
    global dupCount
    dupCount = 0
    jobs = []
    while timeStart < timeEnd:
        # query one day once
        # start from 0 hour and 86400*1000 because timestamp*1000 before
        timeStart = timeStart/timeInterval*timeInterval
        end = timeStart + timeInterval
        if end >= timeEnd:
            end = timeEnd + 1
        jobs.append(gevent.spawn(queryDuplicate, awsauth, endpoint, m_Body,
                                 timeStart, end))
        timeStart = end
    gevent.joinall(jobs)
    logging.info("result:%s", json.dumps(statisticalDict, indent=4))
    statisticalDup(statisticalDict)
    logging.info("duplication log count:%r", dupCount)

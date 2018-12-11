# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import sys
reload(sys)
sys.setdefaultencoding('utf8')

import pymongo
from csdn_spider.items import CsdnSpiderItem
from csdn_spider.settings import MONGO_STR
from csdn_spider.spiders.blogspider import r, p
client = pymongo.MongoClient(MONGO_STR)

blogt = client.csdn.blog
tagt = client.csdn.tag

def replace_htmlUncode(s):
    s = s.replace('&quot;', '"')
    s = s.replace('&amp;', '&')
    s = s.replace('&lt;', '<')
    s = s.replace('&gt;', '>')
    s = s.replace('&nbsp;', ' ')
    s = s.replace('\\\'', '\'')
    return s

def replace_htmlEncode(s):
    s = s.replace('"', '&quot;')
    s = s.replace('&', '&amp;')
    s = s.replace('<', '&lt;')
    s = s.replace('>', '&gt;')
    s = s.replace(' ', '&nbsp;')
    s = s.replace('\\', '\\\\')
    s = s.replace('\'', '\\\'')
    return s

def encode(s):
    s = s.replace('\\', '\\\\')
    s = s.replace('\'', '\\\'')
    s = s.replace('\t', '')
    s = s.replace('\n', '')
    return s


class CsdnSpiderPipelineMongo(object):
    def process_item(self, item, spider):
        if isinstance(item, CsdnSpiderItem):
            _id = item.get('_id')
            title = item.get('title')
            writer = item.get('writer')
            # read = item.get('read')
            tags = item.get('tags')
            time = item.get('time')
            original = item.get('original')
            content = item.get('content')
            """
            数据写入
            tag处理成数字，去重
            博客内容入库
            """
            tagnew = []
            for tag in tags:
                ok = r.sismember('csdn:blog:tags', tag)
                if not ok:
                    p.sadd('csdn:blog:tags', tag)
                    ret = tagt.insert({'tag':tag,'count':1,'ids':[[writer,_id]]})
                    tagnew.append(ret)
                else:
                    ret = tagt.update({'tag':tag},{'$inc':{'count':1},'$push':{'ids':[writer,_id]}},False,False)
                    ret = tagt.find_one({'tag': tag},{'_id':1})
                    tagnew.append(ret['_id'])
            tags = tagnew

            ret = blogt.insert({'bid':_id,'title':encode(title),'uid':writer,'tags':tags,
                          'time':time,'content':encode(str(content)),'original':original})
            # print(ret)

        return ''

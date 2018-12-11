#!/usr/bin/python
# -*-coding:utf-8-*-

import json
import sys
from scrapy.spiders import Spider
from scrapy.http import Request
import logging
from csdn_spider.settings import BLOGKEY, USERKEY, BLOGKEYOK, REDIS_HOST, REDIS_PORT, REDIS_DB, BLOGFILE_DIR
from collections import defaultdict
from csdn_spider.util.util import getresponsejson

# import urlparse
reload(sys)
sys.setdefaultencoding('utf8')

import hiredis
import redis

pool = redis.ConnectionPool(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
r = redis.StrictRedis(connection_pool=pool)
p = r.pipeline()

d = defaultdict(int)


# 爬首页各大类文章列表，保存进redis start_url
class BlogTypeSpider(Spider):
    name = "blogtype"
    # allowed_domains = ["blog.csdn.net"]
    start_urls = [
        'https://blog.csdn.net/api/articles?type=more&category=ai',
        'https://blog.csdn.net/api/articles?type=more&category=cloud',
        'https://blog.csdn.net/api/articles?type=more&category=blockchain',
        'https://blog.csdn.net/api/articles?type=more&category=db',
        'https://blog.csdn.net/api/articles?type=more&category=career',
        'https://blog.csdn.net/api/articles?type=more&category=engineering',
        'https://blog.csdn.net/api/articles?type=more&category=arch',
        'https://blog.csdn.net/api/articles?type=more&category=fund',
    ]

    def __init__(self, *args, **kwargs):
        # Dynamically define the allowed domains list.
        domain = kwargs.pop('domain', '')
        self.allowed_domains = filter(None, domain.split(','))
        super(BlogTypeSpider, self).__init__(*args, **kwargs)

    def parse(self, response):
        """

        去重的策略
        url ---博客url
        id -- 博客id
        uid -- 博主id
        if id 不在 csdn:user:uid 集合里，把sadd csdn:user:uid id ，url 加到csdn:blog列表内
        """
        bodyjs = json.loads(getresponsejson(response))
        # print(json.dumps(bodyjs, indent=4, ensure_ascii=False))
        category = response.request._url.split('=')[-1]
        f = open('%s%s.txt' % (BLOGFILE_DIR, category), 'a+')
        status = bodyjs['status']
        next_link = response.request._url
        if status == 'true':
            articles = bodyjs['articles']
            fl = len(articles)
            if fl > 0:
                d[next_link] += fl
                logging.info('%s articles is %d' % (next_link, d[next_link],))
                for article in articles:
                    # 处理博客内容
                    _id = article['id']
                    uid = article['url'].split('/')[3]
                    f.write(article['url'] + '\n')
                    p.sadd('category:%s' % category, int(_id))
                    #去重操作
                    ok = r.sismember('csdn:user:%s' %(uid,), _id)
                    uok = r.keys('csdn:user:%s' %(uid,))
                    if not ok:
                        p.sadd('csdn:user:%s' %(uid,),_id)
                        if not uok:
                            p.lpush(USERKEY, 'https://blog.csdn.net/%s' % (uid,))
                        p.lpush(BLOGKEY, article['url'])
                        logging.info('%s ==== %s ' % (article['url'], _id))
                    else:
                        logging.info('*********%s ==== %s ********** is ok ' % (article['url'], _id))
                    p.execute()
                f.flush()
                f.close()
                yield Request(url=next_link, callback=self.parse, dont_filter=True)

            else:
                logging.info('%s articles is 0' % (next_link,))
        else:
            logging.info(' %s status is false!!!!!!!' % (next_link,))

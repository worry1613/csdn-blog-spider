#!/usr/bin/python
# -*-coding:utf-8-*-

import json
import sys
from scrapy.spiders import Spider
from scrapy.http import Request
import logging
from settings import BLOGKEY, USERKEY, BLOGKEYOK, REDIS_HOST, REDIS_PORT, REDIS_DB, BLOGFILE_DIR
from collections import defaultdict
from util.util import getresponsejson

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
        #
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
                    f.write(article['url'] + '\n')
                    p.sadd('category:%s' % category, int(_id))
                    ok = r.sismember(BLOGKEYOK, int(_id))
                    if not ok:
                        p.lpush(BLOGKEY, article['url'])
                        # p.sadd(BLOGKEYOK, int(_id))
                        logging.info('%s ==== %d ' % (article['url'], int(_id)))
                    else:
                        logging.info('*********%s ==== %d ********** is ok ' % (article['url'], int(_id)))
                f.flush()
                f.close()
                p.execute()
                yield Request(url=next_link, callback=self.parse, dont_filter=True)

            else:
                logging.info('%s articles is 0' % (next_link,))
        else:
            logging.info(' %s status is false!!!!!!!' % (next_link,))

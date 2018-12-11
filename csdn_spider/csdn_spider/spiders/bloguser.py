# -*- coding: utf-8 -*-
# @创建时间 : 10/12/2018 
# @作者    : worry1613(549145583@qq.com)
# GitHub  : https://github.com/worry1613
# @CSDN   : http://blog.csdn.net/worryabout/
from scrapy_redis.spiders import RedisSpider
import json
import urlparse
import sys
import datetime
import time
from bs4 import BeautifulSoup
from scrapy.spiders import Spider
from scrapy.http import Request
from scrapy_redis.spiders import RedisSpider
import logging
from csdn_spider.settings import BLOGKEY, USERKEY, BLOGKEYOK, REDIS_HOST, REDIS_PORT, REDIS_DB, BLOGFILE_DIR

reload(sys)
sys.setdefaultencoding('utf8')

from blogtypespider import r, p

class BlogUserSpider(RedisSpider):
# class BlogUserSpider(Spider):
    name = "bloguser"
    # allowed_domains = ["blog.csdn.net"]
    redis_key = USERKEY
    # start_urls = ['https://blog.csdn.net/qq_41841569',
    #               'https://blog.csdn.net/Mprog',
    #               'https://blog.csdn.net/yihanzhi',
    #               'https://blog.csdn.net/Cymbals',
    #               'https://blog.csdn.net/xiuya19',
    #               'https://blog.csdn.net/u5a75',
    #               'https://blog.csdn.net/u011263983/']

    def __init__(self, *args, **kwargs):
        # Dynamically define the allowed domains list.
        domain = kwargs.pop('domain', '')
        self.allowed_domains = filter(None, domain.split(','))
        super(BlogUserSpider, self).__init__(*args, **kwargs)

    def parse(self,response):
        """
        不做数据处理，只是找到博客url，写入redis
        :param response:
        :return:
        """
        logging.info(response.url)
        try:
            page = int(response.url.split('/')[-1])
        except :
            page = 1
        data = response.body
        soup = BeautifulSoup(data, "html5lib")
        # pages = soup.find_all(class_='ui-pager')

        urls = soup.find_all(class_='article-item-box')

        for url in urls:
            u = url.find('a').get('href')
            print(u)
            bs = u.split('/')
            bid = bs[-1]
            uid = bs[3]
            # 统一去重策略
            ok = r.sismember('csdn:user:%s' % (uid,), bid)
            if not ok:
                p.sadd('csdn:user:%s' % (uid,), bid)
                p.lpush(BLOGKEY, url)
                logging.info('%s ==== %d ' % (u, int(bid)))
            else:
                logging.info('*********%s ==== %d ********** is ok ' % (u, int(bid)))
            p.execute()
        lens = len(urls)
        if lens > 20:
            page +=1
            if 'article' in response.url:
                s = response.url.split('/')
                s[-1] = str(page)
                url = '/'.join(s)
            else:
                url = response.url + '/article/list/%d' % (page,)

            yield Request(url=url, callback=self.parse, dont_filter=True)





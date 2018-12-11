# -*- coding: utf-8 -*-
# @创建时间 : 8/12/2018 
# @作者    : worry1613(549145583@qq.com)
# GitHub  : https://github.com/worry1613
# @CSDN   : http://blog.csdn.net/worryabout/

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
from csdn_spider.items import CsdnSpiderItem

reload(sys)
sys.setdefaultencoding('utf8')

from blogtypespider import r, p

# class BlogSpider(Spider):
class BlogSpider(RedisSpider):
    name = "blog"
    # allowed_domains = ["blog.csdn.net"]
    redis_key = BLOGKEY
    # start_urls = ['https://blog.csdn.net/Yt7589/article/details/84867706',
    #               'https://blog.csdn.net/mfcing/article/details/7330581',
    #               'https://blog.csdn.net/Bryan__/article/details/51229032',
    #               'https://blog.csdn.net/yang_daxia/article/details/84722469',
    #               'https://blog.csdn.net/xuexijiaqq3533076323/article/details/84718841',
    #               'https://blog.csdn.net/worryabout/article/details/79784838',
    #               'https://blog.csdn.net/G15738290530/article/details/51830464',
    #               'https://blog.csdn.net/u010046908/article/details/61916389',
    #               'https://blog.csdn.net/goldenfish1919/article/details/78280051',
    #               'https://blog.csdn.net/jiaoyangwm/article/details/79570864',
    #               'https://blog.csdn.net/Gupaoxueyuan/article/details/78994652',
    #               'https://blog.csdn.net/u010205879/article/details/79745194']

    def __init__(self, *args, **kwargs):
        # Dynamically define the allowed domains list.
        domain = kwargs.pop('domain', '')
        self.allowed_domains = filter(None, domain.split(','))
        super(BlogSpider, self).__init__(*args, **kwargs)

    def parse(self,response):
        #处理博客内容
        logging.info(response.url)
        data = response.body
        soup = BeautifulSoup(data, "html5lib")

        art = CsdnSpiderItem()
        title = soup.find_all(class_='title-article')[0].getText().strip()
        _id = int(response.url.split('/')[-1])
        writer = response.url.split('/')[3]
        # txt = soup.find_all(id="article_content")[0].getText().strip()
        content = soup.find_all(id="article_content")[0]
        art['_id'] = _id
        art['title'] = title.replace('  ','').replace('\n','')
        art['writer'] = writer
        # art['text'] = txt
        art['content'] = content

        dts = str(soup.find_all(class_="time")[0].getText()).strip()        #2017年10月19日 08:59:24
        dt = datetime.datetime.strptime(dts, "%Y年%m月%d日 %H:%M:%S")
        ts = int(time.mktime(dt.timetuple()))
        # read = int(soup.find_all(class_="read-count")[0].getText().strip()[4:])     # 阅读数：14438
        tags = []
        if len(soup.find_all(class_="tag-link"))>0:                 #tags 标签
            for tag in soup.find_all(class_="tag-link"):
                t = tag.getText().strip()
                tags.append(t)
        original = 0                #原创 转载
        if len(soup.find_all(class_="article-type type-1 float-left"))>0:
            if soup.find_all(class_="article-type type-1 float-left")[0].getText().strip() == '原':
                original = 1
        art['time'] = ts
        # art['read'] = read
        art['tags'] = tags
        art['original'] = original
        yield art

        # 处理用户信息,加到userkey列表中，不做处理在user爬虫中再处理
        ok = r.keys('csdn:user:%s' % (writer,))
        if not ok:
            r.lpush(USERKEY, 'https://blog.csdn.net/%s' % (writer,))
            logging.info('user--%s ======' % (writer,))

        #处理博客内容下面的推荐列表
        users = []
        for u in soup.find_all(class_="recommend-item-box"):            #博客推荐
            if u.find_all('a'):
                url = u.find_all('a')[0].get('href')
                uid = url.split('/')[3]
                _id = url.split('/')[-1]

                #统一去重策略
                ok = r.sismember('csdn:user:%s' % (uid,), _id)
                uok = r.keys('csdn:user:%s' % (uid,))
                if not ok:
                    p.sadd('csdn:user:%s' % (uid,), _id)
                    if not len(uok):
                        p.lpush(USERKEY, 'https://blog.csdn.net/%s' % (uid,))
                    p.lpush(BLOGKEY, url)
                    logging.info('%s ==== %s ' % (url, _id))
                else:
                    logging.info('*********%s ==== %s ********** is ok ' % (url, _id))
                p.execute()
# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class CsdnSpiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    """
    blog内容
    """
    _id = scrapy.Field()        #blog id
    title = scrapy.Field()      #blog title
    time = scrapy.Field()       #blog create time
    tags = scrapy.Field()       #blog tags
    read = scrapy.Field()       #blog read
    content = scrapy.Field()    #blog main content
    writer = scrapy.Field()     #blog writer id
    original = scrapy.Field()   #blog 是否原创

class CsdnSpiderUserItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    """
    blog 作者
    """
    _id = scrapy.Field()
    # user = scrapy.Field()
    pv = scrapy.Field()         #访问
    fen = scrapy.Field()        #积分
    rank = scrapy.Field()       #排名
    level = scrapy.Field()      #等级
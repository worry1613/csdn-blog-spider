#!/usr/bin/python
# -*- coding: utf-8 -*-

def getresponsejson(response):
    if response._body[0] == '{' and response._body[-1] == '}':
        return response._body
    start = response._body.find('(') + 1
    bodystr = response._body[start:-1]
    # ret = json.loads(bodystr)
    return bodystr
#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'g0335'

import requests

def GET(url):
    try:
        data = requests.get(url, verify=False)
        print "GET %s: %d" % (url, data.status_code)
        if data.status_code == 200 or data.status_code == 201:
            return data.json()
        else:
            return []
    except Exception,e:
        print "GET %s : %s" % (url, e.message)

def DEL(url):
    try:
        data = requests.delete(url, verify=False)
        print "DEL %s: %d" % (url, data.status_code)
        if data.status_code == 200 or data.status_code == 201:
            return data.json()
        else:
            return []
    except Exception,e:
        print "DEL %s : %s" % (url, e.message)

def PUT(url, data={}):
    try:
        data = requests.put(url, data=data, verify=False)
        print "PUT %s: %d" % (url, data.status_code)
        if data.status_code == 200 or data.status_code == 201:
            return data.json()
        else:
            return []
    except Exception,e:
        print "PUT %s : %s" % (url,e.message)

def POST(url, data={}):
    try:
        data = requests.post(url, data=data, verify=False)
        print "POST %s: %d" % (url, data.status_code)
        if data.status_code == 200 or data.status_code == 201:
            return data.json()
        else:
            return []
    except Exception,e:
        print "POST %s : %s" % (url, e.message)
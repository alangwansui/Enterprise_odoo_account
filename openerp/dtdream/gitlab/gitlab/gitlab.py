#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'g0335'

import requests


class DTGitLab(object):
    def __init__(self, url, token):
        if self.__check_url(url):
            if url.endswith('/'):
                self.__url = url + 'api/v3'
            else:
                self.__url = url + '/api/v3'
            self.__toke = token
        else:
            raise Exception('Error URL Params')

    def __check_url(self, url):
        import re
        if re.match(r"^(http)[s]?(:\/\/)[\w\-.]+[\/]?$", url) is None:
            return False
        return True

    def get_url(self):
        return self.__url

    def get_token(self):
        return self.__toke



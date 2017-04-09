#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'g0335'

import sys
import ConfigParser
import string, os

class CONF(object):
    def __init__(self, filename):
        self.__file = filename
        cf = ConfigParser.ConfigParser()
        cf.read(self.__file)
        self.__src_url   = cf.get("src", "url").strip()
        self.__src_token = cf.get("src", "token").strip()
        self.__groups    = cf.get("src", "groups").strip()
        self.__personal_space = cf.get("src", "user").strip()
        # self.__projects  = cf.get("src", "projects").strip()

        self.__dst_url   = cf.get("dst", "url").strip()
        self.__dst_token = cf.get("dst", "token").strip()

        self.__user = cf.get("info", "user").strip()
        self.__email = cf.get("info", "email").strip()

    def get_src_url(self):
        return self.__src_url

    def get_src_token(self):
        return self.__src_token

    def get_groups(self):
        if self.__groups:
            return self.__groups.split(',')
        return []

    def get_personal_space(self):
        return self.__personal_space

    # def get_projects(self):
    #     if self.__projects:
    #         return self.__projects.split(',')
    #     return []

    def get_dst_url(self):
        return self.__dst_url

    def get_dst_token(self):
        return self.__dst_token

    def get_user_name(self):
        return self.__user

    def get_user_email(self):
        return self.__email
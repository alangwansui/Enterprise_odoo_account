#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'g0335'

import requests
from gitlab import DTGitLab
from openerp.dtdream.gitlab.utils import DTHttps

class DTProject(DTGitLab):
    def __init__(self, url, token):
        super(DTProject, self).__init__(url, token)

    def get_groups(self):
        url = "%s/groups?private_token=%s" % (self.get_url(), self.get_token())
        data = DTHttps.GET(url)
        groups = []
        if data:
            for group in data:
                groups.append({'id': group['id'], 'name': group['name']})
        return groups

    def get_group(self, id=-1):
        url = "%s/groups/%d?private_token=%s" % (self.get_url(), id, self.get_token())
        return DTHttps.GET(url)

    def get_group_by_name(self, name):
        for group in self.get_groups():
            if group['name'] == name:
                return self.get_group(group['id'])
        return []

    def create_group(self, name, path, des=""):
        url = "%s/groups?private_token=%s" % (self.get_url(), self.get_token())
        data = {
            'name':name,
            'path':path,
            'description': des
        }
        return DTHttps.POST(url, data=data)

    def is_group_exsit(self, name):
        for group in self.get_groups():
            if name == group['name']:
                return True
        return False

    def delete_group(self, id=-1):
        url = "%s/groups/%d?private_token=%s" % (self.get_url(), id, self.get_token())
        return DTHttps.DEL(url)

    def get_projects(self):
        url = "%s/projects?private_token=%s" % (self.get_url(), self.get_token())
        data =  DTHttps.GET(url)
        projects = self.__wrapper_projects(data)
        return projects

    def get_all_projects(self):
        data_list = []
        i = 0
        baseurl = self.get_url()
        token = self.get_token()
        while True:
            i = i + 1
            url = "%s/projects/all?private_token=%s&per_page=100&page=%s" % (baseurl, token, i)
            data = DTHttps.GET(url)
            data_list += data
            if len(data) < 100:
                break
        projects = self.__wrapper_projects(data_list)
        return projects

    def is_project_exsit(self, name, namespace_name):
        for prj in self.get_projects():
            if name == prj['name'] and namespace_name == prj['namespace_name']:
                return True
        return False

    def __wrapper_projects(self, data):
        projects = []
        if data:
            for prj in data:
                projects.append({'id': prj['id'],
                                 'name': prj['name'],
                                 'http_url_to_repo': prj['http_url_to_repo'],
                                 'ssh_url_to_repo': prj['ssh_url_to_repo'],
                                 'namespace_id': prj['namespace']['id'],
                                 'namespace_name': prj['namespace']['name'],
                                 'visibility_level': prj['visibility_level']})
        return projects

    def get_projects_by_group(self, id):
        # url = "%s/groups/%d/projects?private_token=%s" % (self.get_url(), id, self.get_token())
        # data = DTHttps.GET(url)
        data = self.get_group(id)
        projects = self.__wrapper_projects(data['projects'])
        return projects

    def get_project(self, id=-1):
        url = "%s/projects/%d?private_token=%s" % (self.get_url(), id, self.get_token())
        return DTHttps.GET(url)

    def get_project_by_name_and_group(self, name, namespace_name):
        for prj in self.get_projects():
            if prj['name'] == name and prj['namespace_name'] == namespace_name:
                return self.get_project(prj['id'])
        return []

    def create_project(self, name, namespace_id=None, visibility_level=None):
        url = "%s/projects?private_token=%s" % (self.get_url(), self.get_token())
        data = {
            'name': name,
            'namespace_id': namespace_id,
            'visibility_level': visibility_level
        }
        return DTHttps.POST(url,data=data)

    def delete_project(self, id=-1):
        url = "%s/projects/%d?private_token=%s" % (self.get_url(), id, self.get_token())
        return DTHttps.DEL(url)

if __name__ == '__main__':
    URL = "https://gitlab04.dtdream.com"
    TOKEN = "xxxxx"
    prj = DTProject(URL, TOKEN)
    group = prj.get_group_by_name('zongke')
    for p in prj.get_projects_by_group(group['id']):
        prj.delete_project(p['id'])
    prj.delete_group(group['id'])

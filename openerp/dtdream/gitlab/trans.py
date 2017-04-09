#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'g0335'

import sys,os
import subprocess

from conf import CONF
from gitlab.project import DTProject

def clone(url, name):
    old = os.getcwd()
    os.chdir('data')
    try:
        cmd = 'git clone --bare %s' % url
        value = subprocess.call([cmd], shell=True)
        print value
    finally:
        os.chdir(old)

def push(url, project_name):
    old = os.getcwd()
    os.chdir('data/%s' % project_name)
    try:
        cmd = 'git remote rm origin'
        subprocess.call([cmd], shell=True)
        cmd = 'git remote add origin %s' % url
        subprocess.call([cmd], shell=True)
        cmd = 'git push --all --progress origin'
        subprocess.call([cmd], shell=True)
        cmd = 'git push --tags --progress origin'
        subprocess.call([cmd], shell=True)
    finally:
        os.chdir(old)

def trans_appoint_groups(c):
    src_prj = DTProject(c.get_src_url(), c.get_src_token())
    dst_prj = DTProject(c.get_dst_url(), c.get_dst_token())

    _trans_(dst_prj, src_prj, c.get_groups())


def _trans_(dst_prj, src_prj, groups):
    for group in groups:
        if not src_prj.is_group_exsit(group):
            continue
        src_group_info = src_prj.get_group_by_name(group)
        if not dst_prj.is_group_exsit(group):
            dst_prj.create_group(group, group)
        dst_group_info = dst_prj.get_group_by_name(group)

        for prj in src_prj.get_projects_by_group(src_group_info['id']):
            if not dst_prj.is_project_exsit(prj['name'], prj['namespace_name']):
                dst_prj.create_project(prj['name'], dst_group_info['id'], prj['visibility_level'])
            dst_project_info = dst_prj.get_project_by_name_and_group(prj['name'], prj['namespace_name'])
            clone(prj['ssh_url_to_repo'], prj['name']+'.git')
            push(dst_project_info['ssh_url_to_repo'], prj['name']+'.git')


def trans_all_projects(c):
    src_prj = DTProject(c.get_src_url(), c.get_src_token())
    dst_prj = DTProject(c.get_dst_url(), c.get_dst_token())
    g = []
    for group in src_prj.get_groups():
        g.append(group['name'])

    _trans_(src_prj, dst_prj, g)

def trans_all_projects_in_personal_space(c):
    src_prj = DTProject(c.get_src_url(), c.get_src_token())
    dst_prj = DTProject(c.get_dst_url(), c.get_dst_token())
    user = c.get_personal_space()

    for prj in src_prj.get_projects():
        if not prj['namespace_name'] == user:
            continue
        if not dst_prj.is_project_exsit(prj['name'], user):
            dst_prj.create_project(prj['name'])
        dst_project_info = dst_prj.get_project_by_name_and_group(prj['name'], user)
        clone(prj['ssh_url_to_repo'], prj['name'] + '.git')
        push(dst_project_info['ssh_url_to_repo'], prj['name'] + '.git')

def init_git(c):
    cmd = 'git config --global user.name %s' % c.get_user_name()
    subprocess.call([cmd], shell=True)
    cmd = 'git config --global user.email %s' % c.get_user_email()
    subprocess.call([cmd], shell=True)

def check_git():
    value = subprocess.call(['git --version'], shell=True)
    if value != 0 :
        return False
    return True

if __name__ == '__main__':

    if not check_git():
        exit(-1)

    if not os.path.exists('data'):
        os.makedirs('data')

    if len(sys.argv) != 2:
        print "python trans.py {config file}"
    else:
        try:
            file = sys.argv[1]
            c = CONF(file)

            init_git(c)
            if c.get_personal_space():
                trans_all_projects_in_personal_space(c)

            if len(c.get_groups()) > 0:
                trans_appoint_groups(c)
            else:
                trans_all_projects(c)

        except Exception, e:
            print e.message


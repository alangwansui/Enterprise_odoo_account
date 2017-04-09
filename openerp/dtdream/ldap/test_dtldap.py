# -*- coding: utf-8 -*-

__author__ = "g0335"


from dtldap import DTLdap

dtldap = DTLdap()
############################################################
# 测试查询接口
print dtldap.search('h0032')

############################################################
# 测试删除和创建用户接口
# dtldap.delete_user('test2017')
# info = {
#     'displayName':'测试',
#     'mail':'test2017_test2017@dtdream.com',
#     'physicalDeliveryOfficeName':'信息开发部',
#     'telephoneNumber': '12312341234',
#     'passwd':'Abcd_1234'
# }
# dtldap.create_user('test2017', **info)
# print dtldap.search('test2017')
# print dtldap.search('test2017', attr_list=['userAccountControl'])

############################################################
# 测试创建OU和删除OU接口
# dtldap.create_ou('DTTEST')
# dtldap.delete_ou('DTTEST')

############################################################
# 测试创建group和删除group接口
# if dtldap.is_group_exist('DTTEST'):
#     print "exsit"
# else:
#     dtldap.create_group('DTTEST')
#
# print dtldap.search('DTTEST', 'Group')
#
# dtldap.delete_group('DTTEST')
# print dtldap.search('DTTEST', 'Group')


############################################################
# 测试用户是否在指定group群组里
# print dtldap.is_user_in_group('g0335', 'dtmulti')

############################################################
# 测试往指定组里添加成员
# if dtldap.is_group_exist('DTTEST'):
#     print "exist group"
# else:
#     dtldap.create_group('DTTEST')
# print dtldap.search('DTTEST', "Group")
#
# info = {
#     'displayName':'测试',
#     'mail':'test2017_test2017@dtdream.com',
#     'physicalDeliveryOfficeName':'信息开发部',
#     'telephoneNumber': '12312341234'
# }
# if dtldap.is_user_exist('test2017'):
#     print 'exist user'
# else:
#     dtldap.create_user('test2017', **info)
# print dtldap.search('test2017')
#
# if dtldap.is_user_in_group('test2017', 'DTTEST'):
#     print "user in group"
#     dtldap.del_user_from_group('test2017', 'DTTEST')
# else:
#     dtldap.add_user_to_group('test2017', 'DTTEST')
#
# print dtldap.search('test2017', attr_list=['memberOf'])

############################################################
# 测试修改用户属性接口
# print dtldap.search('test2017', attr_list=['displayName', 'mail', 'physicalDeliveryOfficeName', 'telephoneNumber'])
# info={
#     'displayName':'测试2017',
#     'mail':'test2017@dtdream.com',
#     'physicalDeliveryOfficeName':'信息开发部',
#     'telephoneNumber': '78912341234'
# }
# dtldap.modify_user('test2017', **info)
#
# print dtldap.search('test2017', attr_list=['displayName', 'mail', 'physicalDeliveryOfficeName', 'telephoneNumber'])


dtldap.unbind()
# -*- coding: utf-8 -*-
# 销售审批配置类
from openerp import models, fields, api


# 办事处、系统部主管
class dtdream_office_line(models.Model):
    _name = "dtdream.office.line"

    office_line_id = fields.Many2one('dtdream.project.authorize.config')
    office_id = fields.Many2one("dtdream.office", string="办事处")
    office_director = fields.Many2one('hr.employee',string="办事处主任")



class dtdream_system_line(models.Model):
    _name = "dtdream.system.line"

    system_line_id = fields.Many2one('dtdream.project.authorize.config')
    system_id = fields.Many2one("dtdream.industry",string="系统部")
    system_director = fields.Many2one("hr.employee",string="系统部主管")



# 规范性审核
class dtdream_standard_line(models.Model):
    _name = "dtdream.standard.line"

    standard_line_id = fields.Many2one('dtdream.project.authorize.config')
    project_authorize_accessor = fields.Many2one('hr.employee', string="项目授权接口人")


# 审批同意
class dtdream_approval_line(models.Model):
    _name = "dtdream.approval.line"

    approval_line_id = fields.Many2one('dtdream.project.authorize.config')
    approver = fields.Many2one('hr.employee',string="营销管理部人员")


# # 盖章完成
# class dtdream_finish_line(models.Model):
#     _name = "dtdream.finish.line"
#
#     finish_line_id = fields.Many2one('dtdream.project.authorize.config')
#     project_authorize_accessor = fields.Many2one('hr.employee', string="项目授权接口人")


#服务部审批
class dtdream_service_line(models.Model):
    _name = "dtdream.service.line"

    service_line_id = fields.Many2one('dtdream.project.authorize.config')
    project_authorize_service = fields.Many2one('hr.employee', string="服务部")




class dtdream_project_authorize_config(models.Model):
    _name = "dtdream.project.authorize.config"

    name = fields.Char(default="项目申请授权配置")
    office_line =   fields.One2many('dtdream.office.line','office_line_id', string='办事处审批配置')
    system_line = fields.One2many('dtdream.system.line', 'system_line_id', string='系统部审批配置')
    # standard_line      =   fields.One2many('dtdream.standard.line', 'standard_line_id',string='规范性审核')
    # approval_line      =   fields.One2many('dtdream.approval.line', 'approval_line_id',string='审批同意')
    # # finish_line        =   fields.One2many('dtdream.finish.line', 'finish_line_id',string='盖章完成')
    # service_line       =   fields.One2many('dtdream.service.line', 'service_line_id', string='服务部审批')
    fuwu_fawu_config = fields.Many2one('hr.employee', string="服务与法务配置人")
    project_authorize_accessor = fields.Many2one('hr.employee', string="规范性审核")
    project_authorize_service = fields.Many2one('hr.employee', string="服务部审批")
    fawu = fields.Many2one('hr.employee', string="法务")
    approver = fields.Many2one('hr.employee', string="营销管理部")


    # 项目招投标授权
    # 销售
    #
    # 办事处 / 系统部审批
    # 办事处 / 系统部主管
    #
    # 规范性审核
    # 项目授权接口人
    #
    # 审批同意
    # 营销管理部
    #
    # 盖章完成
    # 项目授权接口人

from openerp import models, fields, api, exceptions, tools


class dtdream_expense_batch_approval(models.Model):
    _name = 'dtdream.expense.batch.approval'

    @api.multi
    def expense_batch_approval(self):
        self.env['dtdream.expense.agree.wizard'].btn_confirm()


from odoo import fields, models, api


class CashCollection(models.Model):
    _name = 'cash.collection'
    _rec_name = 'cash_collection_no'

    cash_collection_no = fields.Char("Cash Collection No")
    date = fields.Datetime("Date", default=fields.datetime.now())
    type = fields.Selection([
        ('bill', 'Bill [Diagnosis]')
        , ('bill_others', 'Bill [others]')
        , ('opd', 'OPD')
        , ('admission', 'Admission')
        , ('optics', 'Optics')], 'Type')
    total = fields.Float("Total")
    debit_ac_id = fields.Char("Debit Account")
    credit_ac_id = fields.Char("Credit Account")
    cash_collection_line = fields.One2many("cash.collection.line", "cash_collection_line_id", "Cash Collection")
    state = fields.Selection([
        ('pending', 'Pending'),
        ('approve', 'Confirmed'),
        ('cancel', 'Cancelled')], 'State', default='pending', readonly=True)
    journal_id = fields.Char("Journal ID")

    @api.model
    def create(self, vals):
        record = super().create(vals)
        if record:
            cc_name_text = 'CC-0100' + str(record.id)
            record.update({'cash_collection_no': cc_name_text})
        return record


class CashCollectionLine(models.Model):
    _name = 'cash.collection.line'

    cash_collection_line_id = fields.Many2one("cash.collection", "Cash Collection")
    mr_no = fields.Many2one('money.receipt', "MR No")
    opd_id = fields.Many2one('opd.info', "OPD No")
    bill_id = fields.Many2one('opd.info', "Bill Number")
    admission_id = fields.Many2one('admission.info', "Admission Number")
    amount = fields.Float("Amount")

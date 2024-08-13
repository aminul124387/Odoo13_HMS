from odoo import fields, models, api


class DiscountConfigurationInfo(models.Model):
    _name = 'discount.configuration'
    _rec_name = 'client_name'

    date = fields.Date(string='Date')
    discount_con_id = fields.Char(string='Discount Configuration ID')
    client_name = fields.Char(string='Client Name')
    discount_type = fields.Selection([('fixed', 'Fixed'),
                              ('variance', 'Variance')], default='fixed')
    over_all_discount = fields.Char(string='Over all Discount (%)')
    from_date = fields.Date(string='From Date')
    to_date = fields.Date(string='To Date')

    discount_configure_line_id = fields.One2many('discount.configuration.line', 'discount_configure_item_id')

    @api.model
    def create(self, vals):
        record = super().create(vals)
        if record:
            name_text_admission = 'D_Con-0100' + str(record.id)
            record.update({'discount_con_id': name_text_admission})
        return record



class BillPaymentLine(models.Model):
    _name = 'discount.configuration.line'

    department = fields.Many2one(string='Department', related='item_name.department')
    item_name = fields.Many2one('item.entry', "Test Name", ondelete='cascade')
    applicable = fields.Boolean("Applicable")
    price = fields.Float("Test Fee", related='item_name.price')
    fixed_amount = fields.Float("Fixed Amount")
    amount = fields.Float("Amount(%)")
    after_discount_amount = fields.Float("After Discount Amount")

    discount_configure_item_id = fields.Many2one("discount.configuration", "Information")

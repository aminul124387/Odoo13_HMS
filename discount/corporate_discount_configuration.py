from odoo import fields, models, api


class CorporateDiscountConfigurationInfo(models.Model):
    _name = 'corporate.discount'
    _rec_name = 'client_name'

    date = fields.Date(string='Date')
    corporate_discount_id = fields.Char(string='Discount Configuration ID')
    client_name = fields.Char(string='Client Name')
    discount_type = fields.Selection([('fixed', 'Fixed'),
                              ('variance', 'Variance')], default='fixed')
    over_all_discount = fields.Char(string='Over all Discount (%)')
    from_date = fields.Date(string='From Date')
    to_date = fields.Date(string='To Date')

    corporate_discount_configure_line_id = fields.One2many('corporate.discount.line', 'corporate_discount_configure_item_id')


    @api.model
    def create(self, vals):
        record = super().create(vals)
        if record:
            name_text_admission = 'Cor-Dis-0100' + str(record.id)
            record.update({'corporate_discount_id': name_text_admission})
        return record



class CorporateDiscountItemLine(models.Model):
    _name = 'corporate.discount.line'


    department = fields.Many2one(string='Department', related='item_name.department')
    item_name = fields.Many2one('item.entry', "Test Name", ondelete='cascade')
    applicable = fields.Boolean("Applicable")
    price = fields.Float("Test Fee", related='item_name.price')
    fixed_amount = fields.Float("Fixed Amount")
    amount = fields.Float("Amount(%)")
    after_discount_amount = fields.Float("After Discount Amount")

    corporate_discount_configure_item_id = fields.Many2one("corporate.discount", "Information")

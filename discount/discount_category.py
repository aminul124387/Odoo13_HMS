from odoo import fields, models, api


class Discount_Category_Info(models.Model):
    _name = 'discount.category'
    _rec_name = 'discount_cat_name'

    date = fields.Date(string='Date')
    discount_cat_id = fields.Char(string='Discount ID')
    discount_cat_name = fields.Char(string='Discount Type Name')
    bank_account_name = fields.Char(string='Account Name')
    amount_fixed = fields.Float(string='Amount Fixed')
    amount_percent = fields.Float(string='Amount Percent')
    # payment_type = fields.Many2one('payment.type', string='Payment Type')


    # state = fields.Selection([('approved', 'Approved'),
    #                           ('notapproved', 'Not Approved'),
    #                           ('cancelled', 'Cancelled')], 'Status', default='notapproved',
    #                          readonly=True)





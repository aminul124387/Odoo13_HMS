from odoo import fields, models, api


class AdmissionItemInfo(models.Model):
    _name = 'pharmacy.item'
    _rec_name='product'

    # name = fields.Many2one('admission.info.line', 'Item Name', ondelete='cascade')


    # admission_line_id = fields.One2many('pharmacy.item', 'addmission_item_id')
    product = fields.Char(string='Product')
    price = fields.Char(string='Price')
    quantity = fields.Char(string='Quantity')

    sub_total = fields.Char(string='Sub Total')

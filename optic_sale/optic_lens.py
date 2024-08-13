from odoo import fields, models, api


class OpticLens(models.Model):
    _name = "optic.lens"
    _rec_name = 'lens_name'

    lens_code = fields.Char("Code")
    lens_name = fields.Char("Lens Name")
    purchase_price = fields.Float("Purchase price")
    sell_price = fields.Float("Sale Price")
    lens_type = fields.Selection([
        ('glass', 'Glass')
        , ('plastic', 'Plastic')], "Lens Type", default='plastic')
    supplier = fields.Char("Supplier Name")

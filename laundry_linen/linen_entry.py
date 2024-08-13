from odoo import fields, models, api


class LinenEntry(models.Model):
    _name = 'linen.entry'

    name = fields.Char("Name")
    color = fields.Char('Color')
    quantity = fields.Integer('Quantity')
    type = fields.Selection(
        [('general', 'General Purpose Linen'), ('patient', 'Patient Linen'), ('ward', 'Ward Linen')], string="Type")
    others = fields.Char("Others")

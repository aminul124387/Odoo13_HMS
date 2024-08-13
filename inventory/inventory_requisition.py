from odoo import fields, models, api


class InventoryRequisition(models.Model):
    _name = 'inventory.requisition'

    # date = fields.Date(default=fields.Date.now())
    reference_no = fields.Char("Reference No")
    department = fields.Char()
from odoo import fields, models, api
from odoo.addons.general_hospital_v_03.blood_bank.blood_bank import _
from odoo .addons .sale.models.sale import SaleOrder as CustomSaleOrder

from odoo.exceptions import UserError
from odoo import api, fields, models

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    _description = 'Custom Sale Description'

    sale_descriptions = fields.Char(string='Custom Sale Details')
    partner_mobile = fields.Char(
        related='partner_id.mobile',
        string='Partner Mobile',
        readonly=True
    )


    def unlink(self): # One method to inherit the function for the item delete
        return super(CustomSaleOrder, self).unlink()

    # def unlink(self): # This is the second method for the inherit function to specifice work!
    #     return super().unlink(CustomSaleOrder, self).unlink()
    # CustomSaleOrder.unlink=unlink()
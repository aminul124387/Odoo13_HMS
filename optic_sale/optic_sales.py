import datetime

from odoo import fields, models, api
from odoo.exceptions import UserError


class OpticSaleOrder(models.Model):
    _name = "optics.sale"
    _rec_name = 'optic_sale_id'

    date = fields.Datetime("Date", default=fields.Datetime.now())
    optic_sale_id = fields.Char("Optic Sale ID", readonly=True)
    patient_name = fields.Many2one('patient.info', "Patient Name")
    patient_id = fields.Char(related='patient_name.patient_id', string="Patient Id", readonly=True)
    mobile = fields.Char(string="Mobile", readonly=True, related='patient_name.mobile')
    address = fields.Char("Address", related='patient_name.address')
    age = fields.Char("Age", related='patient_name.age')
    gender = fields.Selection("Gender", related='patient_name.gender')

    right_eye_sph = fields.Char('Right Eye SPH')
    right_eye_cyl = fields.Char('Right Eye CYL')
    right_eye_axis = fields.Char('Right Eye AXIS')
    right_eye_sph_n = fields.Char('Right Eye SPH -N')
    right_eye_cyl_n = fields.Char('Right Eye CYL -N')
    right_eye_axis_n = fields.Char('Right Eye AXIS -N')
    left_eye_sph = fields.Char('Left Eye SPH')
    left_eye_cyl = fields.Char('Left Eye CYL')
    left_eye_axis = fields.Char('Left Eye AXIS')
    left_eye_sph_n = fields.Char('Left Eye SPH -N')
    left_eye_cyl_n = fields.Char('Left Eye CYL -N')
    left_eye_axis_n = fields.Char('Left Eye AXIS -N')
    hard_cover = fields.Boolean("Cover", default=True)
    cell_pad = fields.Boolean("Cell Pad", default=True)
    frame_id = fields.Char('Frame')
    quantity = fields.Integer('Quantity', default=1)
    qty_available = fields.Integer("Stock Quantity", readonly=True)
    price = fields.Float('Price')
    delivery_date = fields.Date(string="Delivery Date")
    optics_sale_line_id = fields.One2many('optics.sale.line', 'optics_sale_id', 'Lens Entry'),
    # optics_sale_payment_line_id = fields.One2many("optics.sale.payment.line", "optics_sale_payment_line_id",
    # "Bill Register Payment")



    card_no = fields.Char('Card No.')
    bank_name = fields.Char('Bank Name')
    status = fields.Selection([
        ('pending', 'Pending')
        , ('confirmed', 'Confirmed')
        , ('cancelled', 'Cancelled')], 'Status', default='pending', readonly=True)


    # Payement wise Field start Here -------------------
    payment_type = fields.Selection([('cash', 'Cash'), ('card', 'Card'), ('m_cash', 'MFS')], default='cash')
    ac_no = fields.Char("A/C No.")
    psn = fields.Many2one('payment.type', string="Payment A/C")
    mcash_mobile_no_payment = fields.Char(string="M-Cash Mobile", placeholder='Enter Last 4 Digit',
                                          attrs={'invisible': [('payment_type', '!=', 'm_cash')]})
    card_no_payment = fields.Char(string="Card Number",
                                  attrs={'invisible': [('payment_type', '!=', 'card')]})

    total_without_discount = fields.Integer("Total Without Discount", digits='Discount')
    discount_percent = fields.Integer("Discount (%)", default=0.0, digits='Discount')
    total = fields.Float("Grand Total")
    other_discount = fields.Integer("Fixed Discount", default=0.0, digits='Discount')
    paid = fields.Float(string="Paid")
    due_amount = fields.Float("Due Amount")

    @api.model
    def create(self, vals):
        record = super().create(vals)
        if record:
            optic_name_text = 'OPT-010' + str(record.id)
            record.update({'optic_sale_id': optic_name_text})
        return record




    def action_confirm(self):
        self.ensure_one()
        if self.status == 'cancelled':
            raise UserError("Cannot Confirmed a cancelled admission.")
        self.status = 'confirmed'


    def action_cancel(self):
        self.ensure_one()
        # if self.status == 'confirmed':
        #     raise UserError("Cannot Cancel a Confirmed admission.")
        self.status = 'cancelled'



class OpticsLensInfo(models.Model):
    _name = 'optics.sale.line'

    lens_name = fields.Many2one("optic.lens", "Lens Name", ondelete='cascade')
    price = fields.Float("Unit Price", related='lens_name.sell_price')
    qty = fields.Integer("Quantity", default=1),
    total_amount = fields.Integer("Total Amount")

# class OpticSalePaymentLine(models.Model):
#     _name = 'optics.sale.payment.line'
#
#     optics_sale_payment_line_id = fields.Many2one('optics.sale', 'bill register payment')
#     date = fields.Datetime("Date")
#     amount = fields.Float('Amount')
#     type = fields.Char('Type')
#     card_no = fields.Char('Card Number')
#     bank_name = fields.Char('Bank Name')
#     money_receipt_id = fields.Many2one('money.receipt', 'Money Receipt ID')

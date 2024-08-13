from odoo import fields, models, api
from odoo.exceptions import UserError

from odoo.addons.general_hospital_v_03.blood_bank.blood_bank import _
from odoo.addons.test_convert.tests.test_env import record
from odoo.exceptions import ValidationError

class OPDTicketInfo(models.Model):
    _name = 'opd.info'
    _rec_name = 'opd_id'

    date = fields.Datetime(string="Date of Birth", default=lambda self: fields.Datetime.now())
    opd_id = fields.Char(string='OPD ID', readonly=True)
    patient_id = fields.Char(string='Patient ID', related="opd_name.patient_id", readonly=True)
    # patient_name = fields.Many2one('patient.info', "Patient Name")
    opd_name = fields.Many2one('patient.info', string="Patient Name", required=True)

    # ------------------ OPD Relation =====================================
    opd_ticket_line_id = fields.One2many('opd.info.line', 'opd_ticket_item_line_id', required=True)
    # ---------------------- Guarantor Relation

    address = fields.Char(string='Address', related="opd_name.address")
    age = fields.Char(string="Age", related="opd_name.age")
    # gender = fields.Char(string= 'Gender')
    gender = fields.Selection(related='opd_name.gender', store=True)
    mobile = fields.Char(string='Mobile', related="opd_name.age")
    referred_by = fields.Many2one('doctors.profile', "Referred By")
    state = fields.Selection([('draft', 'Draft'),
                              ('created', 'created'),
                              ('confirmed', 'Confirmed'),
                              ('cancelled', 'Cancelled')], 'Status', default='draft',
                             readonly=True)

    # Payement wise Field start Here -------------------
    payment_type = fields.Selection([('cash', 'Cash'), ('card', 'Card'), ('m_cash', 'MFS')], default='cash')
    ac_no = fields.Char("A/C No.")
    psn = fields.Many2one('payment.type', string="Payment A/C")
    mcash_mobile_no_payment = fields.Char(string="M-Cash Mobile", placeholder='Enter Last 4 Digit',
                                          attrs={'invisible': [('payment_type', '!=', 'm_cash')]})
    card_no_payment = fields.Char(string="Card Number",
                                  attrs={'invisible': [('payment_type', '!=', 'card')]})
    # ----------------------------------------------------------------------------------------------

    receipt_id = fields.Char(string='Receipt Id')
    paid = fields.Integer(string='Total', compute='_compute_total')
    # paid_amount = fields.Char(string='Paid Amount')


    @api.model
    def create(self, vals):
        record = super().create(vals)
        if record:
            name_text_opd = 'OPD-1000' + str(record.id)
            record.update({'opd_id': name_text_opd, 'state': 'created'})

        return record

    # =====================================================================

    # =========================================================================


    def customer_confirm(self):
        self.ensure_one()
        if self.state == 'cancelled':
            raise UserError("Cannot Confirmed a cancelled admission.")
        self.state = 'confirmed'
        mr_value = {}
        if self.paid > 0:
            mr_value = {
                'date': self.date,
                'opd_id': self.id,
                'paid': self.paid,
                'payment_type': 'cash'
            }
        # Save changes to the database
        self.env.cr.commit()
        mr_obj = self.env['money.receipt'].create(mr_value)

    # This function used opd ticket Cancelled with Money receipt Cancelled
    def customer_cancel(self):
        self.ensure_one()
        if self.state == 'cancelled':
            raise UserError('Bill is already cancelled.')
        self.state = 'cancelled'
        money_receipts = self.env['money.receipt'].search([('opd_id', '=', self.id)])
        money_receipts.write({'state': 'cancelled'})
        return True
    # --------------------------------------------------  Note book menu Iten code ----------------
    # ========================This function is used for show the total value  ==============================
    @api.depends('opd_ticket_line_id.opd_fees')
    def _compute_total(self):
        for rec in self:
            paid = sum(rec.opd_ticket_line_id.mapped('opd_fees'))
            rec.paid = paid
    # --========================================== Guarantor Line  Code ===================================



        # This Function is used for Patient ID Generate ==============================

        # This Function is used for the field Name show with the Customer ID Generate

    # @api.model
    # def name_get(self):
    #     res = []
    #     for record in self:
    #         patient_name = record.patient_name
    #         opd_id = record.opd_id or '--'
    #         res.append((record.id, f"{patient_name} {opd_id}"))
    #     return res
    # =========================================================================


class OPDLineInfo(models.Model):
    _name = 'opd.info.line'

    doctor_dept_name = fields.Char(string='Department', related='ticket_item_name.doctor_dept_name')
    opd_fees = fields.Integer(string='Price', related='ticket_item_name.opd_fees')
    # -------------------------------- Relation change please ---------
    ticket_item_name = fields.Many2one("opd.item", string="Item Name", ondelete='cascade')
    opd_ticket_item_line_id = fields.Many2one('opd.info', "Information", required=True)



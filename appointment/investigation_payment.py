from odoo import fields, models, api


class AppointmentPaymentInfo(models.Model):
    _name = 'appointment.investigation.payment'
    _rec_name = 'app_investigation_payment_id'


    app_investigation_payment_id = fields.Char(string='Appointment Payment ID', readonly=True)
    calculate_start_date = fields.Date(string='Calculate Start Date')
    calculate_end_date = fields.Date(string='Calculate End Date')
    doctor_name = fields.Many2one('doctors.profile', "Doctor Name")

    appointment_investigation_payment_line_id = fields.One2many('appointment.investigation.payment.line', 'appointment_investigation_payment_item_id')
    # ----------------------------------------------------------------------------------------------
    total_discount = fields.Integer(string='Total Discount')
    total_payable_amount = fields.Integer(string='Total Payable Amount')
    total_billing_amount = fields.Integer(string='Total Billing Amount')
    total_test_all_billing_amount = fields.Integer(string='Total Test in All Billing Amount')
    paid_amount = fields.Integer(string='Paid Amount')
    state = fields.Selection([('pending', 'Pending'),
                              ('pay', 'Pay'),
                              ('done', 'Done'),
                              ('cancelled', 'Cancelled')], 'state', default='pending',
                             readonly=True)
    @api.model
    def create(self, vals):
        record = super().create(vals)
        if record:
            name_text_app = 'AP-0400/' + str(record.id)
            record.update({'app_investigation_payment_id': name_text_app,'state': 'done'})
        return record

    # This Function is used for the field Name show with the Customer ID Generate
    # @api.model
    # def name_get(self):
    #     res = []
    #     for record in self:
    #         opd_name = record.opd_name
    #         opd_id = record.opd_id or '--'
    #         res.append((record.id, f"{opd_name}{' / '} {opd_id}"))
    #     return res

    # =========================================================================

    # --------------------------------------------------  Note book menu Iten code ----------------
    # =============================================================================================
    # --========================================== Guarantor Line  Code ===================================

    # This Fuction is used for the Cancel Button ===========================
    def action_cancel(self):
        self.ensure_one()
        self.state = 'cancelled'

    def action_pay(self):
        self.ensure_one()
        self.state = 'pay'

    def action_done(self):
        self.ensure_one()
        self.state = 'done'

        # This Function is used for Patient ID Generate ==============================



        # This Function is used for the field Name show with the Customer ID Generate

class AppointmentPaymentLineId(models.Model):
    _name = 'appointment.investigation.payment.line'


    item_name = fields.Many2one('item.entry', string="Item Name", ondelete='cascade')
    appointment_investigation_payment_item_id = fields.Many2one("appointment.investigation.payment", "Information")

    discount_amount = fields.Char(string="Discount Amount")
    test_amount = fields.Char(string="Test Amount")
    quantity = fields.Char(string="Quantity")
    mou_payable_amount = fields.Char(string="Mou Payable Amount(%)")
    mou_payable_fixed = fields.Char(string="Mou Payable Fixed")
    mou_max_cap_amount = fields.Char(string="Mou Max Cap Amount")
    after_discount_amount = fields.Char(string="After Dis. Amount")
    payable_amount = fields.Char(strng='Payable Amount')




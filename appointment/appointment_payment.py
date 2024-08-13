from odoo import fields, models, api


class AppointmentPaymentInfo(models.Model):
    _name = 'appointment.payment'
    _rec_name = 'app_payment_id'


    app_payment_id = fields.Char(string='Appointment Payment ID', readonly=True)
    calculate_start_date = fields.Date(string='Calculate Start Date')
    calculate_end_date = fields.Date(string='Calculate End Date')
    doctor_name = fields.Many2one('doctors.profile', "Doctor Name")

    appointment_payment_line_id = fields.One2many('appointment.payment.line', 'appointment_payment_item_id')
    # ----------------------------------------------------------------------------------------------
    total_payable_amount = fields.Char(string='Total Payable Amount')
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
            record.update({'app_payment_id': name_text_app,'state': 'done'})
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

class AppointmentPaymentPine_id(models.Model):
    _name = 'appointment.payment.line'


    patient_name = fields.Many2one('appointment.booking', string="Patient Name", ondelete='cascade')
    appointment_payment_item_id = fields.Many2one("appointment.payment", "Information")

    patient_status = fields.Char(string='Patient Status')
    date = fields.Date(string='Date')
    app_id = fields.Char(string='Appointment ID', related='patient_name.app_id')
    amount = fields.Char(string='Amount', related='patient_name.amount')




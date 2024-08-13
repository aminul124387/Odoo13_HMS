from odoo import fields, models, api


class Appointment_Paid_Info(models.Model):
    _name = 'appointment.paid'
    _rec_name = 'app_payment_id'


    app_payment_id = fields.Char(string='Appointment Payment ID', readonly=True)
    patient_status = fields.Selection([('new', 'New Patient'),
                              ('review', 'Review')], 'patient_status', default='new',
                             readonly=True)
    # ----------------------------------------------------------------------------------------------
    amount = fields.Char(string='Amount')

    @api.model
    def create(self, vals):
        record = super().create(vals)
        if record:
            name_text_app = 'AP-0400/' + str(record.id)
            record.update({'app_payment_id': name_text_app,'patient_status': 'review'})
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

    def action_reach(self):
        self.ensure_one()
        self.state = 'reached'

    def action_done(self):
        self.ensure_one()
        self.state = 'done'

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



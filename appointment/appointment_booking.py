from odoo import fields, models, api
from io import BytesIO
from odoo import http
from odoo.http import request

from odoo.exceptions import ValidationError

from odoo import exceptions


class AppointmentBookingInfo(models.Model):
    _name = 'appointment.booking'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'app_id'
    _order = "app_id desc"

    app_id = fields.Char(string='Appointment ID', readonly=True)
    patient_id = fields.Char(string='Patient ID', related="patient_name.patient_id", readonly=True)
    patient_name = fields.Many2one('patient.info', string="Patient Name", tracking=True)
    # patient_id = fields.Many2one('patient.info', "Patient")
    age = fields.Char(string="Age", related="patient_name.age")
    # ------------------ Pharmacy Item Relation =====================================

    pharmacy_medicine_line_ids = fields.One2many('appointment.pharmacy.line', 'pharmacy_item_id', required=True)
    # prescription_line_id = fields.One2many('appointment.prescription.line', 'prescription_item_id', required=True)
    prescriptions = fields.Html("Prescriptions")
    # ---------------------- Guarantor Relation

    # gender = fields.Char(string= 'Gender')
    gender = fields.Selection(related='patient_name.gender')
    mobile = fields.Char(string='Mobile', related="patient_name.age")
    address = fields.Char(string='Address', related="patient_name.address")
    doctor_id = fields.Many2one('doctors.profile', "Doctor Name", domain=[('state', '=', 'active')])
    app_datetime = fields.Datetime(string="Appointment Time")

    state = fields.Selection([('pending', 'Pending'),
                              ('reached', 'Reached'),
                              ('done', 'Done'),
                              ('cancelled', 'Cancelled')], 'State', default='pending',
                             readonly=True)

    patient_status = fields.Selection([('new', 'New Patient'),
                                       ('review', 'Review')],
                                      string='Patient Status',
                                      default='new',
                                      readonly=True)
    # ----------------------------------------------------------------------------------------------

    invoice = fields.Selection([('draft', 'Draft'),
                                ('Create_invoice', 'Create Invoice')], 'invoice', default='draft',
                               readonly=True)
    reference = fields.Char(string='Reference')
    booking_date = fields.Date(string='Booking Date')
    duration = fields.Integer(string='Duration', default='1')
    urgency_level = fields.Selection([('normal', 'Normal'),
                                      ('urgent', 'Urgent')],
                                     string='Urgency Level',
                                     default='normal')
    amount = fields.Char(string='Amount', tracking=True)

    hbv_infection = fields.Boolean(string='HBV Infection')

    remarks = fields.Text(string='Remarks')
    # This code is for the Cancel Function
    cancel_ids = fields.One2many('cancel.appointment', 'cancel_app_id', string='Cancellation Records')
    cancel_reason = fields.Text(string="Cancel Reason")
    cancel_date = fields.Date(string='Cancel Date', default=fields.Date.today())
    cancel_approved_by = fields.Char('Approved By')
    # ---------------------


    # This code is used for the  Appointment ID Generate   ---------------------

    # @api.model
    # def create_appointment_wizard(self):
    #     """ Onboarding step for company basic information. """
    #     action = self.env.ref('general_hospital_v_03.create_appointment_wizard').read()[0]
    #     # action['res_id'] = self.env.user.company_id.id
    #     return action

    @api.model
    def create(self, vals):
        record = super().create(vals)
        if record:
            name_text_app = 'App-0200' + str(record.id)
            record.update({'app_id': name_text_app, 'state': 'reached'})
        return record

    # ------- This Function is used for maintain the serial Number for the Pharmacy medicine Item ---------------

    @api.onchange('pharmacy_medicine_line_ids')  #
    def onchange_pharmacy_medicine_line_ids(self):  #
        sl_no = 0  #
        for line in self.pharmacy_medicine_line_ids:
            sl_no += 1
            line.sl_no = sl_no

    # ================================== This Function is used for the Change of Patient Status =======================================

    @api.onchange('patient_name')# This is for the patient status check by field of is_company
    def onchange_patient(self):
        if self.patient_name:
            if self.patient_name.is_company:
                self.patient_status = 'review'
            else:
                self.patient_status = 'new'

    # --------------------------------------------------  Cancel Button Function Work ----------------

    def cancel_appointment_show_btn(self):
        if self.state == 'cancelled':
            raise exceptions.UserError("This Appointment is Already Cancelled")
        ir_model_data = self.env['ir.model.data']
        template_id = ir_model_data.get_object_reference('general_hospital_v_03', 'view_cancel_model_form')[1]
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_id': template_id,
            'res_model': 'cancel.appointment',
            'target': 'new',
            'context': {
                'default_cancel_model_type': 'appointment',
                'default_cancel_app_id': self.id,
            }
        }

    def cancel(self):
        self.write({
            'state': 'cancelled',
            'cancel_reason': self.cancel_reason,
            'cancel_date': fields.Date.today(),
        })
        return True


    # --========================================== Guarantor Line  Code ===================================

    def create_invoice(self):
        self.ensure_one()
        self.invoice = 'Create_invoice'

        # This Fuction is used for the Cancel Button ===========================

    # def action_cancel(self):
    #     self.ensure_one()
    #     self.state = 'cancelled'

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


class PharmacyItemLineInfo(models.Model):
    _name = 'appointment.pharmacy.line'

    product = fields.Many2one('pharmacy.item', string='Product', ondelete='cascade')
    price = fields.Char(string='Price', related='product.price')
    quantity = fields.Char(string='Quantity')
    sl_no = fields.Integer(string='S.N.')

    sub_total = fields.Char(string='Sub Total')
    pharmacy_item_id = fields.Many2one('appointment.booking', "Pharmacy")

# class Prescription_Line_Info(models.Model):
#     _name = 'appointment.prescription.line'
#
#     prescriptions_id = fields.Many2one('appointment.prescription.line', "Prescriptions ID", ondelete='cascade')
#     prescriptions = fields.Html("Prescriptions")
#     prescription_item_id = fields.Many2one('appointment.booking', "Prescription")

from odoo import fields, models, api
from odoo.addons.general_hospital_v_03.blood_bank.blood_bank import _


class CreateAppointmentWizard(models.TransientModel):
    _name = 'create.appointment.wizard'
    _description = 'Create Appointment Wizard'
    _rec_name = 'patient_name'

    app_datetime = fields.Date(string='Appointment Date')
    patient_id = fields.Many2one('patient.info', string='Patient', required=True)
    patient_name = fields.Char(string='Patient Name', related='patient_id.name', store=True)
    doctor_id = fields.Many2one('doctors.profile', string="Doctor Name")
    gender = fields.Selection(related='patient_id.gender')
    mobile = fields.Char(string='Mobile', related='patient_id.age')
    address = fields.Char(string='Address', related='patient_id.address')
    patient_status = fields.Selection([('new', 'New Patient'), ('review', 'Review')],
                                      string='Patient Status',
                                      default='new',
                                      readonly=True)

    def button_action_create_appointment(self):
        vals = {
            'patient_name': self.patient_id.id,
            'doctor_id': self.doctor_id.id,
            'app_datetime': self.app_datetime,
        }

        if self.patient_id.is_company:
            vals['patient_status'] = 'review'
        else:
            vals['patient_status'] = 'new'

        appointment_rec = self.env['appointment.booking'].create(vals)

        patient_record = self.patient_id
        patient_record.message_post(body="Appointment Created Successfully!", subject="Appointment")

    @api.model
    def default_get(self, fields_list):
        defaults = super(CreateAppointmentWizard, self).default_get(fields_list)
        active_id = self._context.get('active_id')
        ap_active_id = self._context.get('ap_active_id')
        patient_data = self.env['patient.info'].browse(active_id)
        apt_data = self.env['appointment.booking'].browse(ap_active_id)

        if 'patient_id' in fields_list:
            defaults['patient_id'] = patient_data.id
        if 'patient_name' in fields_list:
            defaults['patient_name'] = patient_data.name

        if 'patient_status' in fields_list:
            defaults['patient_status'] = apt_data.patient_status

        return defaults







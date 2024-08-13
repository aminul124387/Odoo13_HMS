from odoo import fields, models, api


class PatientReportWizard(models.TransientModel):
    _name = 'patient.report.wizard'
    _description = 'Print Patient Wizard Report'

    patient_id = fields.Many2one('patient.info', string="Patient ID")
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ], default='male')
    age = fields.Char(string='Age')
    # address = fields.Char(string='Address')


    def action_btn_patient_report_info(self):
        data = {
            'form_data': self.read()[0],

        }
        return self.env.ref('general_hospital_v_03.patient_details_report_action').report_action(self, data=data)




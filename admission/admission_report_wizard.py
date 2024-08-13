from odoo import fields, models, api


class AdmissionPatientReport(models.TransientModel):
    _name = 'admission.report.wizard'
    _description = 'Print Admission Wizard Report'


    # address = fields.Char(string='Address')
    # user_id = fields.Many2one('res.users', string = "Admitted By")
    patient_id = fields.Many2one('patient.info', string = "Patient Name")
    # patient_name = fields.Many2one('patient.info', string = "Patient Name")
    admission_id = fields.Many2one('admission.info', string = "Admission ID:")
    start_date = fields.Datetime(string = "Start Date")
    end_date = fields.Datetime(string = "End Date")

    # def action_btn_admission_report_info(self):
    #     data = {
    #         'form_data': self.read()[0],
    #     }
    #     return self.env.ref('general_hospital_v_03.admission_details_report_action').report_action(self, data=data)

    def action_btn_admission_report_info(self):
        domain = []
        patient_name = self.patient_id
        if patient_name:
            domain += [('patient_name', '=', patient_name.id)]
        start_date = self.start_date
        if start_date:
            domain += [('date', '>=', start_date)]
        end_date = self.end_date
        if end_date:
            domain += [('date', '<=', end_date)]

        admissions = self.env['admission.info'].search(domain)
        admissions_list = []
        for admission in admissions:

            vals = {
                'admission_id': admission.admission_id,
                'patient_name': admission.patient_name.name,
                'date': admission.date,
                'operation_date': admission.operation_date,
                'referred_by': admission.referred_by.name,
                'referral': admission.referral.broker_name,
                'total': admission.total,
                'due_amount': admission.total,
                'state': admission.state,
                'user_id': admission.user_id.name

            }
            # import pdb
            # pdb.set_trace()
            admissions_list.append(vals)

        data = {
            'form_data': self.read()[0],
            'admissions': admissions_list
        }
        return self.env.ref('general_hospital_v_03.admission_details_report_action').report_action(self, data=data)



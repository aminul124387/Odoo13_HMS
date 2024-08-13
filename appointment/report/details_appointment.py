from odoo import fields, models, api


class AppointmentPatientReport(models.TransientModel):
    _name = 'appointment.report.wizard'
    _description = 'Print Appointment Wizard Report'

    patient_id = fields.Many2one('patient.info', string="Patient")
    date_from = fields.Date(string= "Date Form:")
    date_to = fields.Date(string= "Date To:")
    # app_id = fields.Char(string='Appointment ID')
    # Create pdf report wizard from wizard report_wizard

    def btn_datewisereport_admission(self):
        domain = []
        patient_name = self.patient_id
        if patient_name:
            domain += [('patient_name', '=', patient_name.id)]
        date_from = self.date_from
        if date_from:
            domain += [('booking_date', '>=', date_from)]
        date_to = self.date_to
        if date_to:
            domain += [('booking_date', '<=', date_to)]

        appointments = self.env['appointment.booking'].search(domain)
        appointments_list = []
        for appointment in appointments:
            vals = {
                'app_id': appointment.app_id,
                'age': appointment.age,
                'amount': appointment.amount,
                'duration': appointment.duration,
                'state': appointment.state,
                'app_datetime': appointment.app_datetime
            }
            appointments_list.append(vals)

        data = {
            'form_data': self.read()[0],
            'appointments': appointments_list
        }
        return self.env.ref('general_hospital_v_03.appointment_details_print_report_action').report_action(self, data=data)

    # def btn_datewisereport_admission(self):
    #     patient_id = self.patient_id.id
    #     date_from = self.date_from
    #     date_to = self.date_to
    #
    #     query = """
    #         SELECT app_id, age, app_datetime, doctor_id, amount, duration, state
    #         FROM appointment_booking
    #         WHERE (%s IS NULL OR patient_id = %s)
    #             AND (%s IS NULL OR app_datetime >= %s)
    #             AND (%s IS NULL OR app_datetime <= %s)
    #     """
    #
    #     params = [patient_id, patient_id, date_from, date_from, date_to, date_to]
    #
    #     self._cr.execute(query, params)
    #     appointments = self._cr.dictfetchall()
    #
    #     data = {
    #         'form_data': self.read()[0],
    #         'appointments': appointments
    #     }
    #
    #     return self.env.ref('general_hospital_v_03.date_select_report_admission_action').report_action(self, data=data)


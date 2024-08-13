from datetime import datetime, date

from odoo import fields, models, api
from odoo.exceptions import ValidationError


class Blood_Bank_Donor(models.Model):
    _name = 'blood.donor'
    _rec_name = 'donor_name'

    donor_name = fields.Char('Donor Name')
    date_of_birth = fields.Date(string='Date of Birth')
    age = fields.Integer(string='Age:', readonly=True, compute='_compute_donor_age')
    mobile_no = fields.Char('Mobile No')
    blood_donation_date = fields.Datetime('Received Date', default=fields.Datetime.now())
    description = fields.Text('Description')
    blood_group = fields.Selection([
        ('a+', 'A+')
        , ('a-', 'A-')
        , ('b+', 'B+')
        , ('b-', 'B-')
        , ('ab+', 'AB+')
        , ('ab+', 'AB-')
        , ('o+', 'O+')
        , ('o+', 'O-')], 'Blood Group')
    cost = fields.Float('Cost')
    expired_date = fields.Date('Expired Date')


    @api.depends('date_of_birth')
    def _compute_donor_age(self):
        '''Method to calculate student age'''
        current_dt = date.today()
        for rec in self:
            if rec.date_of_birth:
                start = rec.date_of_birth
                age_calc = ((current_dt - start).days / 365)
                # Age should be greater than 0
                if age_calc > 0.0:
                    rec.age = age_calc
            else:
                rec.age = 0


def _(param):
    pass


    @api.constrains('date_of_birth')
    def check_age(self):
        '''Method to check age should be greater than 5'''
        current_dt = date.today()
        if self.date_of_birth:
            start = self.date_of_birth
            age_calc = ((current_dt - start).days / 365)
            # Check if age less than required age
            if age_calc < self.school_id.required_age:
                raise ValidationError(_('''Age of student should be greater \
    than %s years!''' % (self.school_id.required_age)))



class Blood_Bank_Receiver(models.Model):
    _name = "blood.receiver"

    buyer_name = fields.Char('Buyer Name')
    receive_date = fields.Datetime('Received on', default=fields.Datetime.now())
    mobile_no = fields.Char('Mobile No')
    patient_name = fields.Many2one('patient.info', string="Patient Name")
    patient_id = fields.Char(string="Patient ID", related='patient_name.patient_id')
    description = fields.Text('Description')
    blood_group = fields.Selection([
        ('a+', 'A+')
        , ('a-', 'A-')
        , ('b+', 'B+')
        , ('b-', 'B-')
        , ('ab+', 'AB+')
        , ('ab+', 'AB-')
        , ('o+', 'O+')
        , ('o+', 'O-')], 'Blood Group')
    price = fields.Float('Price')
    paid_amount = fields.Float('Paid Amount')
    unpaid_amount = fields.Float('Unpaid Amount')

from odoo import fields, models, api
from odoo.tools import datetime

from odoo.exceptions import ValidationError

from odoo import exceptions
from odoo.exceptions import UserError


class CancelModel(models.Model):
    _name = 'cancel.appointment'
    _rec_name = 'cancel_app_id'

    CANCEL_MODEL_TYPES = [
        ('appointment', 'Appointment'),
        ('bill', 'Bill'),
        ('admission', 'admission'),
    ]

    cancel_app_id = fields.Many2one('appointment.booking', string='Appointment ID:')
    cancel_bill_id = fields.Many2one('bill.register', string='Investigation ID:')
    cancel_adn_id = fields.Many2one('admission.info', string='Admission ID:')
    cancel_date = fields.Date(string='Cancel Date', default=fields.Date.today())
    cancel_reason = fields.Text(string="Cancel Reason")
    cancel_approved_by = fields.Many2one('res.users', 'Approved By')
    cancel_model_type = fields.Selection(CANCEL_MODEL_TYPES, string='Cancel Model Type')
    state = fields.Selection([('cancelled', 'Cancelled')], "State")

    def cancel(self):
        if self.state == 'cancelled':
            raise exceptions.UserError('This form is already cancelled.')
        elif not self.cancel_reason:
            raise exceptions.UserError('Give a valid Cancel Reason')
        elif self.cancel_model_type == 'appointment':
            self.cancel_app_id.cancel()
        elif self.cancel_model_type == 'bill':
            self.cancel_bill_id.cancel()
        elif self.cancel_model_type == 'admission':
            self.cancel_adn_id.cancel()
        self.cancel_date = fields.Date.today()
        self.state = 'cancelled'

        return True

    def cancel_appointment(self):
        if self.state == 'cancelled':
            raise exceptions.UserError('This form is already cancelled.')
        elif not self.cancel_reason:
            raise exceptions.UserError('Give a valid Cancel Reason')
        elif self.cancel_model_type == 'appointment':
            self.cancel_app_id.cancel()
        elif self.cancel_model_type == 'bill':
            context = {
                'cancel_reason': self.cancel_reason,
                'cancel_date': self.cancel_date,
                'cancel_approved_by': self.cancel_approved_by.name}
            self.cancel_bill_id.with_context(context).cancel()
        elif self.cancel_model_type == 'admission':
            context = {
                'cancel_reason': self.cancel_reason,
                'cancel_date': self.cancel_date,
                'cancel_approved_by': self.cancel_approved_by.name}
            self.cancel_adn_id.with_context(context).cancel()
        self.cancel_date = fields.Date.today()
        self.state = 'cancelled'

        return True






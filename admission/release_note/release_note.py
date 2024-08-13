from odoo import fields, models, api
from odoo import exceptions


class ReleaseNote(models.Model):
    _name = 'release.note'
    _description = 'Release Note'

    release_note_date = fields.Datetime(string="Date", default=lambda self: fields.Datetime.now())
    release_note_make_by = fields.Many2one('res.users', 'Release Noted By', default=lambda self: self.env.user.id)
    release_note = fields.Text(string="Release Note", placeholder="Give me Valid Release Note for Patient")
    admission_id = fields.Many2one('admission.info', string='Admission ID', readonly=True)
    released_by = fields.Many2one('doctors.profile', string="Released By")
    diagnosis = fields.Many2many('diagnosis.info', string="Diagnosis")
    treatment = fields.Text(string="Hospital Treatment")
    state = fields.Selection([('release', 'Release'),
                              ('created', 'Created'),
                              ('pending', 'Pending'),
                              ('confirmed', 'Confirmed'),
                              ('paid', 'Paid'),
                              ('cancelled', 'Cancelled')], 'State', default='pending',
                             readonly=True, required=True)

    def release_note_update_info(self):
        if self.state == 'cancelled':
            raise exceptions.UserError('This form is already cancelled.')
        elif self.state == 'release':
            raise exceptions.UserError('This form is already cancelled.')
        elif not self.release_note:
            raise exceptions.UserError('Please provide a valid release note.')

        self.ensure_one()

        admission = self.admission_id
        if admission:
            admission.write({
                'release_note': self.release_note,
                'release_note_date': self.release_note_date,
                'release_note_make_by': self.release_note_make_by,
                'diagnosis': self.diagnosis,
                'treatment': self.treatment
            })

        return True

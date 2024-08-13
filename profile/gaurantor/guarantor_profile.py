import string

from odoo import fields, models, api


class GuarantorProfile(models.Model):
    _name = "guarantor.profile"
    _rec_name ='guarantor_name'


    guarantor_id = fields.Char(string="Guarantor ID", readonly=True)
    ref = fields.Char(string='Ref:')
    guarantor_name = fields.Char(string="Guarantor Name")
    guarantor_address = fields.Char(string='Address Details')
    guarantor_relationship = fields.Char(string='Relationship')
    guarantor_contact = fields.Char(string='Contact Details')
    state = fields.Selection([('created', 'Created'),
                              ('notcreated', 'Notcreated')], 'State', default='notcreated',
                             readonly=True)

# ------------------------------------------
    @api.model
    def create(self, vals):
        record = super().create(vals)
        if record:
            name_text = 'Gr-0100' + str(record.id)
            record.update({'guarantor_id': name_text, 'state': 'notcreated'})
        return record
    


    # This Fuction is used for the name first letter capital  ===----------------------------
    @api.onchange('guarantor_name')
    def onchange_name(self):
        self.guarantor_name = string.capwords(self.guarantor_name) if self.guarantor_name else None
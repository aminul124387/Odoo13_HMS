from odoo import fields, models, api


class Diagnosis_Info(models.Model):
    _name = 'diagnosis.info'
    _description = 'Diagnosis Info'
    _rec_name = 'diagnosis'

    diagnosis = fields.Char(string="Diagnosis Name")
    # diagnosis_relation = fields.One2many('release.note', 'diagnosis_line_id', string='Admission Relation')

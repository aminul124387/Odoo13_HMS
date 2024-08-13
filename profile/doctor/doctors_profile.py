import string

from odoo import fields, models, api
from odoo.osv.expression import expression


class DoctorsProfile(models.Model):
    _name = 'doctors.profile'
    _order = "referral_id desc"





    referral_id = fields.Char("Referral Code", readonly=True)
    name = fields.Char("Doctor Name")
    mobile = fields.Char("Mobile Number")
    photo = fields.Binary(string='Photo')
    department = fields.Many2one('department.config','Department')
    designation = fields.Char('Designation')
    degree = fields.Char('Degree')
    type = fields.Selection([
        ('inhouse', 'In house'),
        ('consoled', 'Consoled'),
        ('prttime', 'Part Time'),
        ('outsid', 'Out Side')], string='Type', default='inhouse')
    state = fields.Selection([
        ('active', 'Active'),
        ('inactive', 'Inactive')], string='Status', default='active')
    others = fields.Char("Others")
    commission = fields.Char("Commission")
    commission_rate = fields.Float("Commission Rate (%) ")
    last_commission_calculation_date = fields.Date("Last Commission Calculation Date")
    description = fields.Html("Description:")
    # This field is add Many2many Realtionship for add a broker under the doctor --------------------
    referral_ids = fields.Many2many('broker.profile', 'doctor_referral_rel', 'doctor_id', 'referral_id',
                                    string="Referral Persons")
    # This field is added for the doctor reffered Investigation list show --------------------
    bill_info = fields.One2many('bill.register', 'referred_by', "Bill Register", domain=[('state', '=', 'confirmed')])
    admission_info = fields.One2many('admission.info', 'referred_by', "Admission", domain=[('state', '=', 'confirmed')])

    # ------------------------------------------
    # _sql_constraints = [
    #     ('unique_tag_name', 'unique (name, active)', 'Dr. Name Must Be Unique')
    # ]
    # ------------------------------------------
    @api.model
    def create(self, vals):
        record = super().create(vals)
        if record:
            name_text = 'Doc-020' + str(record.id)
            record.update({'referral_id': name_text, 'state': 'active'})
        return record

# This Function used for the name and id show for appointment and doctor profile
    def name_get(self):
        res = []
        for record in self:
            res.append((record.id, f"{record.name} {' '} {record.referral_id or '--'}"))
        return res
## This Fuction is used for the name first letter capital  ===----------------------------
    @api.onchange('name')
    def onchange_name(self):
        self.name = string.capwords(self.name) if self.name else None


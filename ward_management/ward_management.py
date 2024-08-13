from odoo import fields, models, api
from odoo.exceptions import UserError


class WardManagement(models.Model):
    _name = 'ward.management'
    _rec_name = 'ward_id'

    ward_id = fields.Char(string='Ward ID', readonly=True)
    admission_id = fields.Many2one('admission.info', string='Admission ID')
    bed_available = fields.Char(string='Bed Availability Check')
    add_bed = fields.Char(string="Add Bed No.")
    total_days = fields.Char(string='Total Days of Bed Charge')
    patient_name = fields.Char(string='Patient Name')
    received_date = fields.Datetime(string="Received Date", default=lambda self: fields.Datetime.now())
    received_by = fields.Char(string='Received By:')
    referred_by = fields.Many2one('doctors.profile', string="Referred By")
    ward_name = fields.Selection([
        ('male_ward', 'Male Ward'),
        ('female_ward', 'Female Ward'),
        ('emergency', 'Emergency'),
        ('general', 'General'),
        ('eye', 'Eye'),
    ], default='male_ward')
    package_cate = fields.Selection([
        ('none', 'None'),
        ('icu', 'ICU'),
        ('nicu', 'NICU'),
        ('emergency', 'Emergency'),
        ('general', 'General'),
        ('eye', 'Eye'),
    ], default='none')
    # admission = fields.One2many('admission.info', 'package_name', 'Admission History', required=False)
    # testname= fields.function(_testname, string="Test Name", type='char')

    state = fields.Selection([('created', 'Created'),
                              ('confirmed', 'Confirmed'),
                              ('notcreated', 'Notcreated'),
                              ('cancelled', 'Cancelled')], 'Status', default='notcreated',
                             readonly=True)

    mobile = fields.Char(string='Mobile')
    address = fields.Char(string='Address')

    # ------------------ Admission Line Item Relation --------------------------------------------
    # package_line_id = fields.One2many('ward.info.line', 'package_item_id', required=True)
    # ----------------------------------------------------------------------------------------------

    # This Fuction is used for the Cancel Button =========================== item_cancel
    def action_confirm(self):
        self.ensure_one()
        if self.state == 'cancelled':
            raise UserError("Cannot Confirmed a cancelled admission.")
        self.state = 'confirmed'

    def action_cancel(self):
        self.ensure_one()
        # if self.state == 'confirmed':
        #     raise UserError("Cannot Cancel a Confirmed admission.")
        self.state = 'cancelled'

        # This Function is used for package ID Generate

    @api.model
    def create(self, vals):
        record = super().create(vals)
        if record:
            name_text = 'W-0100' + str(record.id)
            record.update({'ward_id': name_text, 'state': 'created'})
        return record

    @api.onchange('admission_id')
    def onchange_patient_info(self):
        if self.admission_id:
            self.update({
                'patient_name': self.admission_id.patient_name.name,
                'mobile': self.admission_id.patient_name.mobile,
                'address': self.admission_id.patient_name.address
            })

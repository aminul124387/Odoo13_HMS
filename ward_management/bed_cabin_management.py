from odoo import fields, models, api


class WardManagement(models.Model):
    _name = 'bed.cabin'
    _rec_name = 'bed_product'

    bed_cabin_no = fields.Char(string='Bed/Cabin No')
    bed_cabin_id = fields.Char(string='Bed/Cabin ID')
    ward_name = fields.Selection([
        ('emergency', 'Emergency'),
        ('general', 'General'),
        ('male_ward', 'Male Ward'),
        ('female', 'Female Ward'),
        ('normal_cabin', 'General Cabin'),
        ('vip_cabin', 'VIP Cabin'),
    ], string='Wards/Cabin Type', default='male_ward')

    patient_name = fields.Many2one('patient.info',string='Patient Name')
    bed_product = fields.Char(string='Bed/Cabin')
    price = fields.Integer(string='Price Per Day')
    type = fields.Char(string='Gatch Bed')
    telephone = fields.Char(string='Telephone')
    department = fields.Char(string='Department')
    invoice_policy = fields.Char(string='Days Full')
    floor_number = fields.Char(string='Floor Number')
    air_condition = fields.Selection([('ac', 'AC'),
                              ('nonac', 'Non AC')
                             ], 'air_condition', default='nonac')



    state = fields.Selection([('created', 'Created'),
                              ('confirmed', 'Confirmed'),
                              ('notcreated', 'Notcreated'),
                              ('cancelled', 'Cancelled')], 'Status', default='notcreated',
                             readonly=True)


    # ------------------ Admission Line Item Relation --------------------------------------------
    # package_line_id = fields.One2many('ward.info.line', 'package_item_id', required=True)
    # ----------------------------------------------------------------------------------------------


    # This Fuction is used for the Cancel Button =========================== item_cancel
    def customer_cancel(self):
        self.ensure_one()
        self.state = 'cancelled'

    def customer_confirm(self):
        self.ensure_one()
        self.state = 'confirmed'

        # This Function is used for package ID Generate

    @api.model
    def create(self, vals):
        record = super().create(vals)
        if record:
            name_text = 'B/C-0100' + str(record.id)
            record.update({'bed_cabin_id': name_text, 'state': 'created'})
        return record

    @api.model
    def name_get(self):
        res = []
        for record in self:
            bed_product = record.bed_product
            bed_cabin_id = record.bed_cabin_id or '--'
            res.append((record.id, f"{bed_product} {' - '} {bed_cabin_id}"))
        return res

    # @api.onchange('admission_id')
    # def onchange_patient_info(self):
    #     if self.admission_id:
    #         self.update({
    #             'patient_name': self.admission_id.patient_name.name,
    #             'mobile': self.admission_id.patient_name.mobile,
    #             'address': self.admission_id.patient_name.address
    #         })
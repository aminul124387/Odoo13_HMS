import string

from odoo import fields, models, api


class HospitalBrokerProfile(models.Model):
    _name = 'broker.profile'


    broker_id = fields.Char("Broker Code", readonly=True)
    broker_name = fields.Char("Broker Name")
    mobile = fields.Char("Mobile No")
    photo = fields.Binary(string='Photo')
    state = fields.Selection([
        ('active', 'Active'),
        ('inactive', 'Inactive')], string='Status', default='active')
    #bill_info = fields.Char("Bill Register")
    admission_info = fields.Char("Admission Info")
    commission = fields.Char("Commission")
    commission_rate = fields.Float("Commission Rate(%) ")
    last_commission_calculation_date = fields.Date("Last Commission Calculation Date")
        # this field for add doctor for a new broker -----------------------------------
    doctor_ids = fields.Many2many('doctors.profile', 'doctor_referral_rel', 'referral_id', 'doctor_id',
                                  string="Doctors")
    # This field add for added Broker reffered Investigation List Show -------------------------------------
    bill_info = fields.One2many('bill.register', 'referral', "Bill Register", domain=[('state', '=', 'confirmed')])
    #bill_ids = fields.One2many('bill.register', 'referral', domain=[('state', '=', 'confirmed')])
    appointment_count = fields.Integer(string='Appointment', compute='')
    bill_count = fields.Integer(string='Investigation', compute='count_bills')
    # appointment_count = fields.Integer(string='Appointment Count', compute='count_appiontments')
    # app_ids = fields.One2many('appointment.booking', 'broker_id', string='Bills')
    # bill_ids = fields.One2many('bill.register', 'broker_id', string='Bills')
    # bill_count = fields.Integer(string='Bill Count', compute='count_bills')
    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100):
        if args is None:
            args = []
        domain = args + ['|', '|', ('broker_id', operator, name), ('broker_name', operator, name),
                         ('mobile', operator, name)]
        return super(HospitalBrokerProfile, self).search(domain, limit=limit).name_get() #-----------------


    @api.depends('bill_info')   # This Function is Used for the Smart Button Bill Count Info
    def count_bills(self):
        self.bill_count = len(self.bill_info) #-----------------

    @api.model # This Function is used for the Generate Broker ID
    def create(self, vals):
        record = super().create(vals)
        if record:
            name_text = 'Brkr-010' + str(record.id)
            record.update({'broker_id': name_text})
        return record #-----------------


    def name_get(self): #This Function is used for the concatenate broker name and broker
        res = []
        for record in self:
            res.append((record.id, f"{record.broker_name} {' '} {record.broker_id or '--'}"))
        return res #---------------------------

    @api.onchange('broker_name') # This Fuction is used for the name first letter capital
    def onchange_name(self):
        self.broker_name = string.capwords(self.broker_name) if self.broker_name else None
        #-----------------
from odoo import fields, models, api


class JournalReceipt(models.Model):
    _name = 'journal.receipt'
    _rec_name = 'name'
    _order = 'name desc'


    name = fields.Char("Journal")
    date = fields.Date("Date", default=fields.Datetime.now())
    bill_id = fields.Many2one("bill.register", "BIll ID")
    opd_id = fields.Many2one('opd.info', 'OPD ID')
    admission_id = fields.Many2one("admission.info", "Admission ID")
    ipe = fields.Many2one('inventory.info', 'Inventory Info')

    refund_amount = fields.Float("Refund Amount", default=0.0)
    total = fields.Integer("Total Amount")
    paid = fields.Float("Paid Amount")
    adv = fields.Integer(string='Advance')
    # payable_amount = fields.Float("Customer Payable Amount", default=0.0)
    due_amount = fields.Float("Due Amount", default=0.0)

    doctors_payment = fields.Float("Doctors Payment")
    broker_payment = fields.Float("Broker Payment")
    already_collected = fields.Boolean("Already collected")
    partner_id = fields.Many2one('res.users', 'Current User', default=lambda self: self.env.user.id)
    payment_type = fields.Selection([
        ('due_pay', 'Due Payment'),
        ('adv', 'Advance'),
        ('cash', 'Cash'),
        ('refund', 'Refund'),
        ('card', 'Card')], 'Payment Type', default='cash')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='confirmed', track_visibility='onchange')
    bill_jr_id = fields.One2many('journal.relation.line', 'journal_id', string= 'Investigation Journal')
    admission_jr_ids = fields.One2many('admission.billjournal.line', 'journal_id', string= 'Admission Journal')
    ref = fields.Char(string='Ref Customer Payable')


    # Additional fields
    ac_no = fields.Char(string="Card A/C No.")
    psn = fields.Char(string="MFS Payment A/C")
    mcash_mobile_no_payment = fields.Char(string="M-Cash Mobile")
    card_paid = fields.Float("Card Amount")
    card_amount = fields.Float("Card Amount")
    mfs_paid = fields.Float("MFS Amount")
    mfs_amount = fields.Float("MFS Amount")
    cash_paid = fields.Float("Cash Amount")
    cash_amount = fields.Float("Cash Amount")
    card_no_payment = fields.Char(string="Card No.")
    def create(self, vals, context=None):
        if context is None:
            context = {}
        res = super(JournalReceipt, self).create(vals, context)
        return res

    @api.model
    def create(self, vals):
        record = super().create(vals)
        if record:
            jr_name_text = 'JR-3001' + str(record.id)
            record.update({'name': jr_name_text})
        return record

    # def print_receipt(self):
    #     return self.env.ref('lions_Hospital_v_01.report_money_receipt_action_form').report_action(self)
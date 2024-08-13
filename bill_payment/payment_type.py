from odoo import fields, models, api


class PaymentTypeInfo(models.Model):
    _name = 'payment.type'
    _rec_name = 'acc_name'


    pt_id = fields.Char(string='Payment ID', readonly=True)
    acc_name = fields.Char(string='Account Name')
    account_type = fields.Char(string='Cash In A/C Type')
    service_charge_percent = fields.Integer(string='Service Charge(%)')
    service_charge_account = fields.Char(string='A/C No. for Service Charge')
    payment_acc_num = fields.Char(string='Payment A/C No.')

    #active = fields.Boolean(string='Active')
    state = fields.Selection([('created', 'Created'),
                                  ('draft', 'Draft')], 'Status', default='draft',
                                 readonly=True)

    # ---------------------------------------------------------------------------------------------

    # -- This Function are used for the action of button ------------------
    def payment_confirmed(self):
        self.ensure_one()
        self.state = 'confirmed'

    def payment_cancel(self):
        self.ensure_one()
        self.state = 'cancelled'
# -----------------------------------------------------------------------------------------------


        # This Function is used for the field Name show with the Customer ID Generate
    @api.model
    def create(self, vals):
        record = super().create(vals)
        if record:
            name_text_admission = 'PT-0100' + str(record.id)
            record.update({'pt_id': name_text_admission, 'state': 'created'})
        return record
    @api.model
    def name_get(self):
        res = []
        for record in self:
            acc_name = record.acc_name
            pt_id = record.pt_id or '--'
            res.append((record.id, f"{acc_name}{' / '} {pt_id}"))
        return res

#---------------------------------------------------------------------------------------------
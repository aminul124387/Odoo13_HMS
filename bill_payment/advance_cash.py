from odoo import fields, models, api


class PaymentTypeInfo(models.Model):

    _name = 'advance.cash'
    _description = 'This Payment Type Module'
    _rec_name = 'partner_name'


    advc_id = fields.Char(string='Advance Payment Id', readonly=True)
    partner_name = fields.Many2one('res.users', 'Current User', default=lambda self: self.env.user.id)
    purpose = fields.Char(string='Purpose')
    amount = fields.Integer(string='Amount')
    account_cash_bank = fields.Char(string='Cash/Bank Account')
    advc_account = fields.Integer(string='Advance Account')

    active = fields.Boolean(string='Active')
    state = fields.Selection([('created', 'Created'),
                                  ('draft', 'Draft'),
                                  ('confirmed', 'Confirmed'),
                                  ('cancelled', 'Cancelled')], 'Status', default='draft',
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

#==--- This code is used for the id or code generate and also record show top view
    @api.model
    def create(self, vals):
        record = super().create(vals)
        if record:
            name_text = 'Advc-0900' + str(record.id)
            record.update({'advc_id': name_text, 'state': 'created'})
        return record

        # This Function is used for the field Name show with the Customer ID Generate

    # @api.model
    # def name_get(self):
    #     res = []
    #     for record in self:
    #         acc_name = record.acc_name
    #         payment_id = record.payment_id or '--'
    #         res.append((record.id, f"{acc_name}{' / '} {payment_id}"))
    #     return res

#---------------------------------------------------------------------------------------------
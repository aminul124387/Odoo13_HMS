from odoo import fields, models, api


# <field name="name" string="Name" filter_domain="['|',('name','ilike',self),('id','ilike',self)]"/>

class Commission_Payment(models.Model):
    _name = 'commission.payment'
    _rec_name = 'commission_payment_id'

    date = fields.Datetime(string="Commission Payment Date", default=lambda self: fields.Datetime.now())
    commission_payment_id = fields.Char(string='Commission ID', readonly=True)

    name = fields.Many2one('doctors.profile', string='Doctor Name')
    broker_name = fields.Many2one('broker.profile', string='Refferel Name')
    commission = fields.Char(string='Commission')

    debit_account = fields.Char(string='Debit Account')
    credit_account = fields.Char(string='Credit Account')
    payment_period = fields.Char(string='Payment Period')


    paid_amount = fields.Char(string='Paid Amount')
    due_amount = fields.Char(string='Due Amount')
    payment_note = fields.Text(string='Payment Note')





    state = fields.Selection([('created', 'Created'),
                              ('draft', 'Draft'),
                              ('confirmed', 'Confirmed'),
                              ('cancelled', 'Cancelled')], 'state', default='draft',
                             readonly=True)

    # --------------------------------Payment Type Rlation --------------------------------------------------------------



    # def print_report(self):
    #     data = {
    #         'commission.payment': self.id,
    #     }
    #
    #     return self.env.ref('commission.payment.print_report_pdf').report_action(self, data=data)

    # import pdb
    # pdb.set_trace()
    # This Fuction is used for the Cancel Button ===========================
    def action_cancel(self):
        self.ensure_one()
        self.state = 'cancelled'

    def action_confirm(self):
        self.ensure_one()
        self.state = 'confirmed'

        # This Function is used for Patient ID Generate ==============================

    @api.model
    def create(self, vals):
        record = super().create(vals)
        if record:
            name_text_admission = 'Com-Payment-0100' + str(record.id)
            record.update({'commission_payment_id': name_text_admission, 'state': 'created'})
        return record


# --------------------------------------------------  Note book menu Iten code ----------------
# =============================================================================================







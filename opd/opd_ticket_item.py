from odoo import fields, models, api
from odoo.exceptions import ValidationError


# <field name="name" string="Name" filter_domain="['|',('name','ilike',self),('id','ilike',self)]"/>

class OPDTicketItem(models.Model):
    _name = 'opd.item'
    _rec_name = 'ticket_item_name'


    opd_item_id = fields.Char(string='Item ID', readonly=True)
    ticket_item_name = fields.Char(string='OPD Item Name')
    doctor_dept_name = fields.Char(string='Department')

    opd_fees = fields.Integer(string='Fee')
    account_id = fields.Char(string='Account ID')


    state = fields.Selection([('created', 'Created'),
                              ('draft', 'Draft'),
                              ('confirmed', 'Confirmed'),
                              ('cancelled', 'Cancelled')], 'Status', default='draft',
                             readonly=True)

    # --------------------------------Payment Type Rlation --------------------------------------------------------------

    @api.onchange('opd_fees')
    def OnchangeOpdFees(self):
        for record in self:
            if record.opd_fees < 0:
                raise ValidationError('OPD Value cannot be Minus(-)!')

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
            name_text_admission = 'OPD-Item-0100' + str(record.id)
            record.update({'opd_item_id': name_text_admission, 'state': 'created'})
        return record


# --------------------------------------------------  Note book menu Iten code ----------------
# =============================================================================================







from odoo import fields, models, api
from odoo.exceptions import ValidationError


class Discount_Generate_Info(models.Model):
    _name = 'discount.item'
    _rec_name = 'discount_id'
    # _inherit = 'admission.info'

    discount_id = fields.Char(string='Discount Id')
    date = fields.Date(string='Date')
    bill_id = fields.Many2one('bill.register', string='Patient Bill ID')
    admission_id = fields.Many2one('admission.info', string='Patient Admission ID')
    patient_name = fields.Char(string='Patient Name')
    # payment_type = fields.Many2one('payment.type', string='Payment Type')
    mobile = fields.Char(string='Mobile No.')
    state = fields.Selection([('approved', 'Approved'),
                              ('notapproved', 'Not Approved'),
                              ('cancelled', 'Cancelled')], 'Status', default='notapproved',
                             readonly=True)

    pending_discount_line_id = fields.One2many('discount.item.line', 'discount_item_id', required=True)

    total = fields.Float(string='Total Amount', related='admission_id.total')
    due_amount = fields.Float(string='Due Amount', related='admission_id.due_amount')
    other_discount = fields.Float(string='Total Discount', related='pending_discount_line_id.other_discount')
    discount_percent = fields.Float(string='Discount Percent', related='pending_discount_line_id.discount_percent')
    sequence=fields.Integer(string='seq')
    total_without_discount = fields.Float(string='Total Without Discount')

    def action_cancel(self):
        self.ensure_one()
        self.state = 'cancelled'

    # def action_discount_approved(self):
    #     active_id = self._context.get('active_id')
    #     discount_update = self.env['admission.info'].browse(active_id)
    #     vals = {
    #         'discount_percent': self.discount_percent,
    #         'other_discount': self.other_discount,
    #     }
    #     discount_update.write(vals)
    #     self.ensure_one()
    #     self.state = 'approved'
    #     return {
    #         'type': 'ir.actions.do_nothing'  # no close form
    #     }
    def action_discount_approved(self):
        active_ids = self._context.get('active_ids')
        discount_update = self.env['admission.info'].browse(active_ids)

        vals = {
            'discount_percent': self.discount_percent,
            'other_discount': self.other_discount,
            'total': self.total,
            'due_amount': self.due_amount,
        }

        discount_update.write(vals)
        self.ensure_one()
        self.state = 'approved'
        return {
            'type': 'ir.actions.do_nothing'  # no close form
        }


    @api.model
    def create(self, vals):
        record = super().create(vals)
        if record:
            name_text_admission = 'Dis-0100' + str(record.id)
            record.update({'discount_id': name_text_admission, 'state': 'approved'})
        return record

    @api.onchange('admission_id', 'bill_id')# ID base value show that field
    def onchange_patient_info(self):
        if self.admission_id:
            self.update({
                'patient_name': self.admission_id.patient_name.name,
                'mobile': self.admission_id.patient_name.mobile
            })
        elif self.bill_id:
            self.update({
                'patient_name': self.bill_id.patient_name.name,
                'mobile': self.bill_id.patient_name.mobile
            })
        else:
            self.update({
                'patient_name': False,
                'mobile': False
            })


    # def discount_amount_aproved(self):
    #     active_id = self._context.get('active_id')

# --------------------------------------------------------------------------
class DiscountCategoryLine(models.Model):
    _name = 'discount.item.line'

    date = fields.Char(string='Date')
    discount_cat_id = fields.Char(string='Discount ID', related='discount_cat_name.discount_cat_id')
    bank_account_name = fields.Char(string='Account Name', related='discount_cat_name.bank_account_name')
    other_discount = fields.Float(string='Amount Fixed')
    discount_percent = fields.Float(string='Discount Percent')
    total_discount = fields.Float(string='Total Amount')
    # --------------- Relation with the Discount Category
    discount_cat_name = fields.Many2one("discount.category", "Discount Type Name", ondelete='cascade')
    discount_item_id = fields.Many2one('discount.item', "Information")

    # @api.onchange('discount_percent')
    # def _onchange_discount_percent(self):
    #     if self.discount_percent:
    #         total_without_discount = self.discount_item_id.total_without_discount
    #         discount_amount = total_without_discount * (self.discount_percent / 100.0)
    #         self.total_discount = discount_amount + self.other_discount

from mock.mock import self

from odoo import fields, models, api
from odoo.addons.general_hospital_v_03.blood_bank.blood_bank import _
from odoo.exceptions import ValidationError


class BillRegisterWizard(models.TransientModel):
    _name = 'bill.register.wizard'

    bill_id = fields.Char(string='Bill ID', readonly=True)
    date = fields.Datetime(string="Date", default=lambda self: fields.Datetime.now())
    patient_name = fields.Many2one('patient.info', string='Patient Name')
    patient_id = fields.Char(string="Patient ID", related='patient_name.patient_id')
    referred_by = fields.Many2one('doctors.profile', "Referred By")
    referral = fields.Many2one('broker.profile', "Referral")
    # -----
    total_without_discount = fields.Float("Total Without Discount")
    discount_percent = fields.Float("Discount (%)")
    service_charge = fields.Float("Service Charge")
    other_discount = fields.Float("Fixed Discount")
    # these fields are related to the bill.bill_pay model
    paid = fields.Float(string="Paid")
    total = fields.Float("Grand Total")
    due_amount = fields.Float("Due Amount")
    bill_register_line_id = fields.One2many('bill.register.wizard.lines', 'bill_item_id', 'Bill Lines')

    # @api.depends('bill_register_line_id.total_price', 'bill_register_line_id.sub_total_amount', 'paid',
    #              'total_without_discount', 'other_discount')
    # def _onchange_total_amount(self):
    #     self.total_without_discount = sum(line.total_price for line in self.bill_register_line_id)
    #     grand_total = sum(line.sub_total_amount for line in self.bill_register_line_id)
    #     self.total = grand_total
    #     # self.adv = self.card_amount + self.mfs_amount + self.cash_amount
    #     if self.other_discount:
    #         self.total = self.total - self.other_discount
    #     self.due_amount = self.total - self.paid

    def update_info(self): # This Function is Work to update data
        active_id = self._context.get('active_id') # Active id base data Find -----------
        # print("active_id", active_id)
        wizard_update=self.env['bill.register'].browse(active_id)
        # print("test data------", test_date)
        lst_item = []
        for rec in self.bill_register_line_id:
            lst_item.append((0,0,{# Data append and also store in the data dictionary
                'item_name': rec.item_name.id,
                'department': rec.department.id,
                'price': rec.price,
                'total_price': rec.total_price,
                'quantity': rec.quantity,
                'flat_discount': rec.flat_discount,
                'discount_percent': rec.discount_percent,
                'total_discount': rec.total_discount,
                'sub_total_amount': rec.sub_total_amount
            }))
        wizard_update.bill_register_line_id = [(5,0,0)] # Exist bill item delete
        vals = {# Send item in the Dictionary
            'patient_name':self.patient_name.id,
            # 'patient_id': self.patient_name,
            'referral': self.referral.id,
            'referred_by': self.referred_by.id,
            'total_without_discount': self.total_without_discount,
            'discount_percent': self.discount_percent,
            # 'service_charge': self.service_charge,
            # 'other_discount': self.other_discount,
            'paid': self.paid,
            'total': self.total,
            'due_amount': self.due_amount,
            'bill_register_line_id': lst_item
        }
        wizard_update.write(vals)# Update Dictionary data in the bill.register Model
        return {'type': 'ir.actions.do.nothing'} # wizard form do not close this line of code


    @api.model
    def default_get(self, fields_list):
        defaults = super(BillRegisterWizard, self).default_get(fields_list)
        active_id = self._context.get('active_id')
        bill_data = self.env['bill.register'].browse(active_id)

        if 'bill_id' in fields_list:
            defaults['bill_id'] = bill_data.bill_id
        if 'paid' in fields_list:
            defaults['paid'] = bill_data.paid
        if 'total' in fields_list:
            defaults['total'] = bill_data.total
        if 'due_amount' in fields_list:
            defaults['due_amount'] = bill_data.due_amount

        if 'bill_register_line_id' in fields_list:
            line_defaults = []
            for line in bill_data.bill_register_line_id:
                line_data = {
                    'item_name': line.item_name.id,
                    'department': line.department.id,
                    'price': line.price,
                    'total_price': line.total_price,
                    'quantity': line.quantity,
                    'flat_discount': line.flat_discount,
                    'discount_percent': line.discount_percent,
                    'total_discount': line.total_discount,
                    'sub_total_amount': line.sub_total_amount,
                }
                line_defaults.append((0, 0, line_data))
            defaults['bill_register_line_id'] = line_defaults

        return defaults

class BillRegisterLineWizard(models.TransientModel):
    _name = 'bill.register.wizard.lines'

    # bill_item_id = fields.Many2one('bill.register', "Info")
    bill_item_id = fields.Many2one('bill.register.wizard', "Info")
    item_name = fields.Many2one('item.entry', "Item Name", ondelete='cascade')
    department = fields.Many2one(string='Department', related='item_name.department')
    price = fields.Float("Price", related='item_name.price')
    total_price = fields.Float("Total Price", compute='_compute_qty_price')
    quantity = fields.Float("Quantity", default=1)
    flat_discount = fields.Float("Flat Discount", related='bill_item_id.other_discount')
    discount_percent = fields.Float("Discount Percent", related='bill_item_id.discount_percent')
    total_discount = fields.Float("Total Discount")
    sub_total_amount = fields.Float("Sub Total Amount")

    @api.depends('price', 'quantity', 'discount_percent')
    def _compute_qty_price(self):
        for record in self:
            record.total_price = record.price * record.quantity
            record.total_discount = record.total_price * (record.discount_percent / 100)
            record.sub_total_amount = record.total_price - record.total_discount

            # Check Quantity Validation for Line Item product -----------
            if record.quantity < 0:
                raise ValidationError('Your Product Quantity Cannot Be Negative!')

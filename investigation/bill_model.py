import re
from odoo import fields, models, api
from odoo.exceptions import UserError
from datetime import datetime, timedelta
from odoo.addons.general_hospital_v_03.blood_bank.blood_bank import _
from odoo.addons.test_convert.tests.test_env import record
from odoo.exceptions import ValidationError

from odoo import exceptions


class BillRegister(models.Model):
    _name = 'bill.register'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'bill_id'
    _order = 'bill_id desc'

    date = fields.Datetime(string="Date", default=lambda self: fields.Datetime.now())
    discount_applied = fields.Boolean(string='Discount Applied', default=False)
    bill_id = fields.Char(string='Bill ID', readonly=True)
    admission_id = fields.Many2one('admission.info', string='Admission ID')
    patient_name = fields.Many2one('patient.info', tracking=True)
    patient_id = fields.Char(string="Patient ID", related='patient_name.patient_id')
    age = fields.Char("Age", related="patient_name.age")
    address = fields.Char("Address", related="patient_name.address")
    gender = fields.Selection(related='patient_name.gender')
    mobile = fields.Char("Mobile", related='patient_name.mobile')
    email = fields.Char(string='Email', related="patient_name.email")
    blood_group = fields.Selection(string='Blood Group', related="patient_name.blood_group")
    referred_by = fields.Many2one('doctors.profile', "Referred By", domain=[('state', '=', 'active')])
    referral = fields.Many2one('broker.profile', "Referral", domain=[('state', '=', 'active')])
    delivery_date = fields.Date("Delivery Date")
    # Cancel fields added here ------
    cancel_ids = fields.One2many('cancel.appointment', 'cancel_bill_id', string='Cancellation Records')
    cancel_reason = fields.Text(string="Cancel Reason")
    cancel_date = fields.Datetime(string='Cancel Date')
    cancel_approved_by = fields.Char('Approved By')# ---------

    # Notebook Link Relationship Field Added Here ----------------------------------------
    bill_register_line_id = fields.One2many('bill.register.line', 'bill_item_id', 'Bill Lines')
    bill_payment_line_id = fields.One2many('bill.paymentline.info', 'billpayment_item_id')
    bill_journal_line_id = fields.One2many('journal.relation.line', 'journal_item_id')
    user_id = fields.Many2one('res.users', 'Current User', default=lambda self: self.env.user.id)


    payment_type = fields.Selection([('cash', 'Cash'),# Payement wise Field start Here -------------------
                                     ('card', 'Card'),
                                     ('m_cash', 'MFS'),
                                     ('card_cash', 'Cash & Card'),
                                     ('m_cash_cash', 'Cash & MFS'),
                                     ('m_cash_card', 'MFS & Card'),
                                     ('card_cash_mcash', 'Cash, Card & MFS')], default='cash')
    ac_no = fields.Char("Card A/C No.")
    psn = fields.Many2one('payment.type', string="MFS Payment A/C")

    mcash_mobile_no_payment = fields.Char(string="M-Cash Mobile", placeholder='Enter Last 4 Digit',
                                          attrs={'invisible': [('payment_type', '!=', 'm_cash')]})
    card_amount = fields.Integer("Card Amount")
    mfs_amount = fields.Integer("MFS Amount")
    cash_amount = fields.Integer("Cash Amount")
    card_no_payment = fields.Char(string="Card Number",
                                  attrs={'invisible': [('payment_type', '!=', 'card')]})
    state = fields.Selection(
        [('pending', 'Pending'), ('paid', 'Full Paid'), ('confirmed', 'Confirmed'), ('cancelled', 'Cancelled')],
        "state", default='pending')

    # ------------------------------------------------------------------------------------------
    # payment_ids = fields.One2many('admission.bill_payment', 'bill_id', string='Payments')
    total_without_discount = fields.Float("Total Without Discount", digits='Discount',
                                          compute='_onchange_total_amount')
    discount_percent = fields.Float("Discount (%)", default=0.0, digits='Discount')
    service_charge = fields.Float("Service Charge")
    other_discount = fields.Float("Fixed Discount", default=0.0, digits='Discount')
    # these fields are related to the bill.bill_pay model

    # amount = fields.Many2one('bill.bill_pay', string='Amount')
    adv = fields.Float(string="Advance")
    paid = fields.Float(string="Paid", tracking=True, default=0.0)
    total = fields.Float("Grand Total", digits='Discount')
    due_amount = fields.Float("Due Amount", digits='Discount', default=0.0)
    bill_payments = fields.One2many('bill.bill_pay', 'bill_id', string='Payments')
    currency_id = fields.Many2one('res.currency', string="Currency",# Currency Generate --------
                                  default=lambda self: self.env['res.currency'].search([('name', '=', 'BDT')]))

    def delete_bill_line_item(self): # This Function is used to delete the bill line item by one click with special command
        if self.state == 'pending':
            self.bill_register_line_id = [(5, 0, 0)]
        else:
            raise UserError(" Cannot Delete the Confirmed Bill Item !")#-----------
        return {
            'effect': { # This code is for the Rainbow image show
                'fadeout': 'fast',
                'type': 'rainbow_man',
                'message': 'Item Has been Successfully Deleted!'
        }
        }
    def action_confirm_bill(self):  # This function use to Confirm and Print report
        if self.state == 'confirmed':
            raise ValidationError("Bill is already confirmed.")
        elif self.state == 'cancelled':
            raise ValidationError("Sorry! You cannot Confirmed the Cancel Bill! ")
        self.state = 'confirmed'
        if self.adv > 0:
            money_receipt = self.env['money.receipt'].create({  # Investigation data transfer to the Money Receipt Model
                'date': self.date,
                'bill_id': self.id,
                'total': self.total,
                'adv': self.adv,
                'due_amount': self.due_amount,
                'ac_no': self.ac_no,
                'psn': self.id,
                'mcash_mobile_no_payment': self.mcash_mobile_no_payment,
                'card_amount': self.card_amount,
                'mfs_amount': self.mfs_amount,
                'cash_amount': self.cash_amount,
                'card_no_payment': self.card_no_payment,
                'payment_type': 'adv'
            })
            payment_vals = {
                'money_receipt_id': money_receipt.id,
                'date': datetime.now(),
                'adv': self.adv,
                'payment_type': 'Advance',  # replace with actual payment type
                'billpayment_item_id': self.id  # link to the bill record
            }
            self.env['bill.paymentline.info'].create(payment_vals)
        jr_payment = self.env['journal.receipt'].create({  # Investigation data transfer to the Journal Receipt Model
            'date': self.date,
            'bill_id': self.id,
            'total': self.total,
            'adv': self.adv,
            'due_amount': self.due_amount,
            'payment_type': 'adv'
        })
        jr_payment_vals = {
            'journal_id': jr_payment.id,
            'journal_item_id': self.id  # link to the bill record
        }
        self.env['journal.relation.line'].create(jr_payment_vals)
        # Save changes to the database
        self.env.cr.commit()
        return self.env.ref('general_hospital_v_03.report_investigation_form').report_action(self)

    def add_payment_btn(self): # Bill Payment Function by click the Add Payment Button
        if self.state == 'pending':
            raise ValidationError("First Confirm the Bill")
        if self.total <= self.paid:
            raise ValidationError("The bill is already Paid")
        ir_model_data = self.env['ir.model.data']
        template_id = ir_model_data.get_object_reference('general_hospital_v_03', 'bill_pay_form_view')[1]
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_id': template_id,
            'res_model': 'bill.bill_pay',
            'target': 'new',
            'context': {
                'default_bill_id': self.id,
                'default_amount': self.paid,
                'default_total': self.total,
                'default_due_amount': self.due_amount,
            }
        }

    def cancel_bill_show_btn(self):  # This function start to cancell form show ------
        if self.state == 'cancelled':
            raise ValidationError("This Bill is already Cancelled!")
        ir_model_data = self.env['ir.model.data']
        template_id = ir_model_data.get_object_reference('general_hospital_v_03', 'view_cancel_model_form')[1]
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_id': template_id,
            'res_model': 'cancel.appointment',
            'target': 'new',
            'context': {
                'default_cancel_model_type': 'bill',
                'default_cancel_bill_id': self.id,
            }
        }

    def cancel(self):
        if self.state == 'cancelled':
            raise exceptions.UserError('This form is already cancelled.')

        # Cancel all related money receipts
        money_receipts = self.env['money.receipt'].search([('bill_id', '=', self.id)])
        money_receipts.filtered(lambda r: r.state != 'cancelled').write({'state': 'cancelled'})
        journal_receipts = self.env['journal.receipt'].search([('bill_id', '=', self.id)])
        journal_receipts.filtered(lambda r: r.state != 'cancelled').write({'state': 'cancelled'})
        # Get the new values for cancel_reason and cancel_approved_by from the action's context
        context = self._context or {}
        cancel_reason = context.get('cancel_reason')
        cancel_approved_by = context.get('cancel_approved_by')

        self.write({
            'state': 'cancelled',
            'cancel_reason': cancel_reason,
            'cancel_approved_by': cancel_approved_by,
            'cancel_date': fields.Date.today(),
        })
        return True



    # ----------------------------------------------------
    @api.model  # This function for the Generate Bill ID---------
    def create(self, vals):
        record = super().create(vals)
        if record:
            bill_name_text = 'Bill-0100' + str(record.id)
            record.update({'bill_id': bill_name_text})
        if not vals.get('bill_register_line_id'):
            raise ValidationError("Please select at least one line item ! Then Save @")
        return record

    # @api.model #This function to update mode validation line item
    # def write(self, vals):
    #     if not vals.get('bill_register_line_id'):
    #         raise ValidationError("Please select at least one item!")
    #     return super(BillRegisterLine, self).create(vals)

    def unlink(self):# This Function is used for the Bill Delete Validation Error!
        for record in self:
            if record.state != 'pending':
                raise ValidationError("You cannot delete the Confirmed Bill!")
        try:
            return super(BillRegister, self).unlink()
        except Exception as e:
            raise ValidationError(_("Something went wrong during the deletion: %s") % str(e))



    def print_invoice(self):  # This Function use tp print invoice -----------
        return self.env.ref('general_hospital_v_03.report_invoice_action').report_action(self)

    # =---- This function is used for Refferel list Show under the Doctor  ----------------------
    @api.onchange('referred_by')
    def onchange_referred_by(self):
        if self.referred_by:
            referral_domain = [('state', '=', 'active'), ('doctor_ids', 'in', self.referred_by.id)]
        else:
            referral_domain = [('state', '=', 'active')]
        return {'domain': {'referral': referral_domain}}

    # =-------------------------------- Validation Error function is added Here  ----------------------
    @api.onchange('paid', 'other_discount', 'discount_percent')
    def check_due_amount(self):
        for record in self:
            # if record.paid or record.other_discount or record.discount_percent or record.total_without_discount or record.due_amount or record.total and not re.match("^[a-zA-Z0-9]+$", record.my_field):
            #     raise ValidationError("Field can only contain alphanumeric characters")
            if record.discount_percent < 0:
                raise ValidationError("Discount Percent Field cannot be negative")
            elif record.due_amount < 0:
                raise ValidationError("Due amount cannot be negative")
            elif record.paid < 0:
                raise self.ValidationError("Paid Value Cannot be Negative")
            elif record.total < 0:
                raise self.ValidationError("Grand Total Cannot ne Negative")
            # Doctor Discount and Discount Percent Validation is on the below:
            elif self.referred_by and self.discount_percent >= 31 or self.discount_percent > 80 or self.discount_percent < 0:
                raise ValidationError(
                    "Give 80% or less Discount OR Cannot provide 30% up Doctor Discount, Please remove Minus value")

    # ----------------------------------  Item Based Calculation Function is end Here -------  ------------------  --------------
    @api.depends('bill_register_line_id.total_price', 'bill_register_line_id.sub_total_amount', 'paid',
                 'total_without_discount', 'other_discount', 'card_amount', 'mfs_amount', 'cash_amount')
    def _onchange_total_amount(self):
        self.total_without_discount = sum(line.total_price for line in self.bill_register_line_id)
        grand_total = sum(line.sub_total_amount for line in self.bill_register_line_id)
        self.total = grand_total
        self.adv = self.card_amount + self.mfs_amount + self.cash_amount
        if self.other_discount or self.adv:
            self.total = self.total - self.other_discount - self.adv
        self.due_amount = self.total - self.paid

    # card_amount = fields.Char("Card Amount")
    # mfs_amount = fields.Char("MFS Amount")
    # cash_amount = fields.Char("Cash Amount")




# -------------------------------------------------------------------------

class BillRegisterLine(models.Model):
    _name = 'bill.register.line'

    bill_item_id = fields.Many2one('bill.register', "Info")
    item_name = fields.Many2one('item.entry', "Item Name", required=True, ondelete='cascade')
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



class BillPaymentLines(models.Model):
    _name = 'bill.paymentline.info'

    money_receipt_id = fields.Many2one('money.receipt', string='Money Receipt', ondelete='cascade')
    bill_pay_id = fields.Many2one('bill.bill_pay', string='Bill Payment')
    date = fields.Datetime(string='Payment Date')
    paid = fields.Float(string='Payment Amount')
    adv = fields.Float(string='Advance')
    payment_type = fields.Char(string='Payment Type')
    card_no_payment = fields.Char(string='Card No.')
    user_id = fields.Many2one('res.users', 'Current User', default=lambda self: self.env.user.id)
    billpayment_item_id = fields.Many2one('bill.paymentline.info', ondelete='cascade')
    due_amount = fields.Float("Due Amount")
class BillJournalRelation(models.Model):
    _name = 'journal.relation.line'

    journal_id = fields.Many2one('journal.receipt', string="Journal ID", ondelete='cascade')
    jr_bill_pay_id = fields.Many2one('bill.bill_pay', string='Bill Payment')
    journal_item_id = fields.Many2one("bill.register", "Information")
    # paid = fields.Integer("Paid Amount")
    # adv = fields.Integer(string='Advance')
    # payment_type = fields.Char(string='Payment Type')
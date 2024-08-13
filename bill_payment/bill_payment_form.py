from odoo import fields, models, api
from odoo.exceptions import ValidationError

from odoo.exceptions import UserError
from datetime import datetime

from odoo.addons.general_hospital_v_03.blood_bank.blood_bank import _
from odoo import exceptions


# -----------------------------------------------------
class InvestigationBillPaymentInfo(models.Model):
    _name = 'bill.bill_pay'

    date = fields.Date(string='Date', required=True, default=datetime.now().strftime('%Y-%m-%d'))
    bill_item_id = fields.Many2one('bill.register', string='Bill Item')
    admission_item_id = fields.Many2one('admission.info', string='Admission Item')
    admission_id = fields.Many2one('admission.info', string='Admission Id')
    bill_id = fields.Many2one('bill.register', string='Bill Id')
    total = fields.Float("Grand Total", related='bill_id.total')
    due_amount = fields.Float("Due Amount")
    amount = fields.Float(string='Amount', default=0.0)
    money_receipt_id = fields.Many2one('money.receipt', 'Money Receipt')
    name = fields.Char("Collection ID")

    status = fields.Selection([('draft', 'Draft'), ('confirmed', 'Confirmed')], string='Status', default='draft')
    # Payment wise Field start Here -------------------
    payment_type = fields.Selection([('cash', 'Cash'),
                                     ('card', 'Card'),
                                     ('m_cash', 'MFS'),
                                     ('card_cash', 'Cash & Card'),
                                     ('m_cash_cash', 'Cash & MFS'),
                                     ('m_cash_card', 'MFS & Card'),
                                     ('card_cash_mcash', 'Cash, Card & MFS')], default='cash')
    ac_no = fields.Char(string="Card A/C No.")
    psn = fields.Many2one('payment.type', string="MFS Payment A/C")

    mcash_mobile_no_payment = fields.Char(string="M-Cash Mobile", placeholder='Enter Last 4 Digit',
                                          attrs={'invisible': [('payment_type', '!=', 'm_cash')]})
    card_paid = fields.Float("Card Amount")
    card_amount = fields.Float("Card Amount")
    mfs_paid = fields.Float("MFS Amount")
    mfs_amount = fields.Float("MFS Amount")
    cash_paid = fields.Float("Cash Amount")
    cash_amount = fields.Float("Cash Amount")
    card_no_payment = fields.Char(string="Card Number",
                                  attrs={'invisible': [('payment_type', '!=', 'card')]})
    # These are used foreign key set with the bill.model money receipt and journal id generate
    bill_payment_mr_line_ids = fields.One2many('bill.paymentline.info', 'bill_pay_id', string='Payment Line')
    bill_payment_jr_line_ids = fields.One2many('journal.relation.line', 'jr_bill_pay_id', string='Journal Payment Line')
    # these are used foreign key set with the admission.info model journal id and money receipt id generate
    admission_payment_mr_line_ids = fields.One2many('hospital_admission.payment.line', 'admission_bill_pay_id',
                                                    string='Admission Mr Payment Lines')
    admission_pay_jr = fields.One2many('admission.billjournal.line', 'admission_pay_jr_ids', string='Admission Jr IDs')

    # Computed Fields
    @api.onchange('card_paid', 'mfs_paid', 'cash_paid')# This Function is used for the total amount calculate
    def _onchange_total_amount(self):
        self.amount = 0
        total_paid_amount = sum(filter(None, [self.card_paid, self.mfs_paid, self.cash_paid]))
        self.amount = total_paid_amount
        # if self.amount > self.due_amount:
        #     raise exceptions.UserError("Paid Amount Cannot be Greater Than Due Amount")
        if self.bill_id:
            self.due_amount = max(self.bill_id.due_amount - total_paid_amount, 0.0)
        elif self.admission_id:
            self.due_amount = max(self.admission_id.due_amount - total_paid_amount, 0.0)

    @api.depends
    def action_pay(self):
        for rec in self:
            value = {
                'date': fields.Datetime.now(),
                'bill_id': rec.bill_id.id if rec.bill_id else False,
                'admission_id': rec.admission_id.id if rec.admission_id else False,
                'paid': 0.0,
                'due_amount': rec.due_amount,
                'payment_type': 'due_pay',
                'ac_no': rec.ac_no,
                'psn': rec.psn.id,
                'mcash_mobile_no_payment': rec.mcash_mobile_no_payment,
                'card_paid': rec.card_paid,
                'mfs_paid': rec.mfs_paid,
                'cash_paid': rec.cash_paid,
                'card_no_payment': rec.card_no_payment,
                # Add other fields as needed
            }

            if rec.amount > 0:
                # Update the due amount and paid amount of the bill register
                if rec.bill_id:
                    bill = self.env['bill.register'].browse(rec.bill_id.id)
                    if bill:
                        rec.due_amount = max(bill.due_amount - rec.amount, 0.0)
                        paid = bill.paid + rec.amount
                        bill.write({
                            'due_amount': rec.due_amount,
                            'paid': paid,
                        })
                        value['paid'] = rec.amount

                        if rec.bill_id.money_receipt_id:
                            money_receipt = self.env['money.receipt'].browse(rec.bill_id.money_receipt_id.id)
                            if money_receipt:
                                money_receipt.due_amount = rec.due_amount

                # Update the due amount and paid amount of the Admission Payment
                elif rec.admission_id:
                    admission = self.env['admission.info'].browse(rec.admission_id.id)
                    if admission:
                        rec.due_amount = max(admission.due_amount - rec.amount, 0.0)
                        paid = admission.paid + rec.amount
                        admission.write({
                            'due_amount': rec.due_amount,
                            'paid': paid,
                        })
                        value['paid'] = rec.amount

                        # Update the due amount in the money.receipt model
                        if rec.admission_id.money_receipt_id:
                            money_receipt = self.env['money.receipt'].browse(rec.admission_id.money_receipt_id.id)
                            if money_receipt:
                                money_receipt.due_amount = rec.due_amount

            if value['paid'] > 0:
                # Create a new money receipt record and link it to the payment line
                mr_obj = self.env['money.receipt'].create(value)
                bill_payment_lines = self.env['bill.paymentline.info'].create({
                    'bill_pay_id': rec.id,
                    'money_receipt_id': mr_obj.id,
                    'date': fields.Datetime.now(),
                    'paid': value['paid'],
                    'due_amount': rec.due_amount,
                    'payment_type': 'due_pay',
                    'billpayment_item_id': rec.id
                })
                # Update the due amount and paid amount of the Investigation Payment
                if rec.bill_id:
                    bill = self.env['bill.register'].browse(rec.bill_id.id)
                    if bill:
                        bill.due_amount = rec.due_amount
                        bill.paid += rec.amount
                admission_payment_line = self.env['hospital_admission.payment.line'].create({
                    'admission_bill_pay_id': rec.id,
                    'money_receipt_id': mr_obj.id,
                    'date': fields.Datetime.now(),
                    'paid': value['paid'],
                    'due_amount': rec.due_amount,
                    'payment_type': 'due_pay',
                    'payment_item_id': rec.id
                })

                # Update the due amount and paid amount of the Admission Payment
                if rec.admission_id:
                    admission = self.env['admission.info'].browse(rec.admission_id.id)
                    if admission:
                        admission.due_amount = rec.due_amount
                        admission.paid += rec.amount

                # Create a new journal receipt record and link it to the payment line
                jr_obj = self.env['journal.receipt'].create(value)
                jr_payment_line = self.env['journal.relation.line'].create({
                    'jr_bill_pay_id': rec.id,
                    'journal_id': jr_obj.id,
                    'journal_item_id': rec.id
                })
                jr_admission_payment_line = self.env['admission.billjournal.line'].create({
                    'admission_pay_jr_ids': rec.id,
                    'journal_id': jr_obj.id,
                    'admission_journal_item_id': rec.id
                })

            rec.state = 'paid'
            rec.due_amount = max(rec.due_amount - rec.amount, 0.0)
            rec.paid = rec.paid + value['paid']

            # Set billpayment_item_id to null before deleting the record
            bill_payment_lines

    @api.model
    def create(self, vals):
        payment_id = super().create(vals)
        if payment_id and vals.get('date'):
            amount = vals.get('amount')
            value = {
                'date': vals['date'],
                'bill_id': vals.get('bill_id'),
                'admission_id': vals.get('admission_id'),
                'paid': amount,
                'due_amount': vals.get('due_amount'),
                # 'due_payment': vals.get('due_payment'),  # Add due_payment field here
                'payment_type': 'due_pay',
                'ac_no': vals.get('ac_no'),
                'psn': vals.get('psn'),
                'mcash_mobile_no_payment': vals.get('mcash_mobile_no_payment'),
                'card_paid': vals.get('card_paid'),
                'mfs_paid': vals.get('mfs_paid'),
                'cash_paid': vals.get('cash_paid'),
                'card_no_payment': vals.get('card_no_payment'),
                # Add other fields as needed
            }

            mr_obj = self.env['money.receipt'].create(value)
            jr_obj = self.env['journal.receipt'].create(value)

            # Update the due and paid amounts in the bill.register model and create payment lines in the bill.payment.line and journal.relation.line models
            if vals.get('bill_id'):
                bill = self.env['bill.register'].browse(vals['bill_id'])
                if bill.due_amount is None:
                    bill.due_amount = 0.0
                if amount and bill.due_amount >= amount:
                    bill.write({'due_amount': max(bill.due_amount - amount, 0.0), 'paid': bill.paid + amount})
                # elif amount and bill.due_amount < amount:
                #     raise UserError(_('Amount is greater than due amount'))

                # Update the due_payment field in the money.receipt model
                if bill.due_amount is not None:
                    mr_obj.due_amount = bill.due_amount

                mr_payment_line_vals = {
                    'billpayment_item_id': vals.get('bill_id'),
                    'date': datetime.now(),
                    'payment_type': 'Due Payment',
                    'paid': amount,
                    'due_amount': vals.get('due_amount'),
                    'money_receipt_id': mr_obj.id,
                }
                mr_payment_line = self.env['bill.paymentline.info'].create(mr_payment_line_vals)
                jr_payment_line_vals = {
                    'journal_item_id': vals.get('bill_id'),
                    'journal_id': jr_obj.id,
                }
                jr_bill_payment_line = self.env['journal.relation.line'].create(jr_payment_line_vals)

            # Update the due and paid amounts in the admission.info model and create payment lines in the hospital_admission.payment.line and admission.billjournal.line models
            elif vals.get('admission_id'):
                admission = self.env['admission.info'].browse(vals['admission_id'])
                if admission.due_amount is None:
                    admission.due_amount = 0.0
                if amount >0 or admission.due_amount >= amount:
                    admission.write(
                        {'due_amount': max(admission.due_amount - amount, 0.0), 'paid': admission.paid + amount})
                # elif amount and admission.due_amount < amount:
                #     raise UserError(_('Amount is greater than due amount'))

                mr_admission_payment_line_vals = {
                    'payment_item_id': vals.get('admission_id'),
                    'date': datetime.now(),
                    'payment_type': 'Due Payment',
                    'paid': amount,
                    'due_amount': vals.get('due_amount'),
                    'money_receipt_id': mr_obj.id,
                }
                admission_payment_line_mr = self.env['hospital_admission.payment.line'].create(
                    mr_admission_payment_line_vals)
                jr_admission_payment_line_vals = {
                    'admission_journal_item_id': vals.get('admission_id'),
                    'journal_id': jr_obj.id,
                }
                admission_payment_line_jr = self.env['admission.billjournal.line'].create(
                    jr_admission_payment_line_vals)

        return payment_id



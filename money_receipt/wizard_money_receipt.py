from odoo import fields, models, api
from odoo import exceptions


class WizardMoneyReceipt(models.TransientModel):
    _name = 'money.receipt.wizard'
    _rec_name = 'reverse_mr_id'
    _order = 'reverse_mr_id desc'


    reverse_mr_id = fields.Char("Reverse Mr ID.")
    date = fields.Datetime("Date", default=fields.Datetime.now())
    bill_id = fields.Many2one("bill.register", "BIll ID")
    opd_id = fields.Many2one('opd.info', 'OPD ID')
    admission_id = fields.Many2one("admission.info", "Admission ID")

    total = fields.Integer("Total Amount")
    paid = fields.Float("Paid Amount")
    adv = fields.Float(string='Advance')
    due_amount = fields.Float("Due Amount", default=0.0)
    doctors_payment = fields.Integer("Doctors Payment")
    broker_payment = fields.Integer("Broker Payment")
    already_collected = fields.Boolean("Already collected")
    user_id = fields.Many2one('res.users', 'Current User', default=lambda self: self.env.user.id)
    payment_type = fields.Selection([
        ('due_pay', 'Due Payment'),
        ('adv', 'Advance'),
        ('refund', 'Refund'),
        ('cash', 'Cash'),
        ('card', 'Card')], 'Payment Type', default='cash')
    payable_amount = fields.Float("Customer Payable Amount", default=0.0)

    payment_line_ids = fields.One2many('bill.paymentline.info', 'money_receipt_id', string='Bill Payment Receipt')
    admission_payment_line_ids = fields.One2many('hospital_admission.payment.line', 'money_receipt_id', string='Admission Payment Receipt')
    # Cancel Field --------------
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='confirmed', track_visibility='onchange')

    reverse_payment_line_ids = fields.One2many('money.receipt.wizard.lines', 'reverse_mr_item_id', string='Reverse Payment Lines')
    refund_customer_amount = fields.Float(string='Refund Customer Amount:')
    card_paid = fields.Float("Card Amount")
    card_amount = fields.Float("Card Amount")
    mfs_paid = fields.Float("MFS Amount")
    mfs_amount = fields.Float("MFS Amount")
    cash_paid = fields.Float("Cash Amount")
    cash_amount = fields.Float("Cash Amount")

    @api.model
    def default_get(self, field_items):
        default_value = super(WizardMoneyReceipt, self).default_get(field_items)
        active_id = self._context.get('active_id')
        active_model = self._context.get('active_model')

        if active_model == 'admission.info':
            active_record = self.env['admission.info'].browse(active_id)
            field_mappings = {
                'admission_id': active_record.id,
                'total': active_record.total,
                'paid': active_record.paid,
                'payable_amount': active_record.payable_amount,
                'adv': active_record.adv,
                'due_amount': active_record.due_amount,
            }
        elif active_model == 'bill.register':
            active_record = self.env['bill.register'].browse(active_id)
            field_mappings = {
                'bill_id': active_record.id,
                'total': active_record.total,
                'paid': active_record.paid,
                'payable_amount': active_record.payable_amount,
                'adv': active_record.adv,
                'due_amount': active_record.due_amount,
            }
        else:
            return default_value

        for field in field_items:
            if field in field_mappings:
                default_value[field] = field_mappings[field]

        return default_value
    #
    # def customer_refund_payment(self):
    #     active_id = self._context.get('active_id')
    #     active_model = self._context.get('active_model')
    #
    #     if active_model == 'admission.info':
    #         record = self.env['admission.info'].browse(active_id)
    #         paid = record.paid
    #         adv = record.adv
    #         due_amount = record.due_amount
    #         payable_amount = record.payable_amount
    #         cash_amount = record.cash_amount
    #         mfs_amount = record.mfs_amount
    #         card_amount = record.card_amount
    #     elif active_model == 'bill.register':
    #         record = self.env['bill.register'].browse(active_id)
    #         paid = record.paid
    #         adv = record.adv
    #         due_amount = record.due_amount
    #         payable_amount = record.payable_amount
    #         cash_amount = 0.0
    #         mfs_amount = 0.0
    #         card_amount = 0.0
    #     else:
    #         return
    #
    #     refund_amount = min(paid + adv, payable_amount)
    #     adv_refund = min(adv, refund_amount)
    #
    #     # Deduct the refund amount from the adv value first
    #     if adv >= payable_amount:
    #         adv -= payable_amount
    #     else:
    #         payable_amount -= adv
    #         adv = 0.0
    #
    #     # Deduct the remaining refund amount from the paid value
    #     if paid >= payable_amount:
    #         paid -= payable_amount
    #     else:
    #         payable_amount -= paid
    #         paid = 0.0
    #
    #     # due_amount += payable_amount
    #     if active_model == 'admission.info':
    #         record.write({'paid': paid, 'adv': adv, 'due_amount': max(0.0, due_amount - payable_amount),
    #                       'payable_amount': payable_amount,
    #                       'cash_amount': cash_amount, 'mfs_amount': mfs_amount, 'card_amount': card_amount})
    #     elif active_model == 'bill.register':
    #         record.write({'paid': paid, 'adv': adv, 'due_amount': max(0.0, due_amount - payable_amount),
    #                       'payable_amount': payable_amount,
    #                       'cash_amount': cash_amount, 'mfs_amount': mfs_amount, 'card_amount': card_amount})
    #
    #     # Generate reverse money receipt
    #     money_receipt = self.env['money.receipt'].create({
    #         'date': fields.Date.today(),
    #         'bill_id': active_id if active_model == 'bill.register' else False,
    #         'admission_id': active_id if active_model == 'admission.info' else False,
    #         'adv': refund_amount,
    #         'paid': refund_amount,
    #         'due_amount': refund_amount,
    #         'payment_type': 'refund',
    #         # Add other fields as needed
    #     })
    #
    #     # Generate reverse journal entry
    #     journal_entry = self.env['journal.receipt'].create({
    #         'date': fields.Date.today(),
    #         'bill_id': active_id if active_model == 'bill.register' else False,
    #         'admission_id': active_id if active_model == 'admission.info' else False,
    #         'adv': refund_amount,
    #         'paid': refund_amount,
    #         'due_amount': refund_amount,
    #         'payment_type': 'refund',
    #         # Add other fields as needed
    #     })

    def customer_refund_payment(self):
        active_id = self._context.get('active_id')
        active_model = self._context.get('active_model')

        if active_model == 'admission.info':
            record = self.env['admission.info'].browse(active_id)
            paid = record.paid
            adv = record.adv
            due_amount = record.due_amount
            payable_amount = record.payable_amount
            cash_amount = record.cash_amount
            cash_paid = record.cash_paid
            mfs_amount = record.mfs_amount
            mfs_paid = record.mfs_paid
            card_amount = record.card_amount
            card_paid = record.card_paid
        elif active_model == 'bill.register':
            record = self.env['bill.register'].browse(active_id)
            paid = record.paid
            adv = record.adv
            due_amount = record.due_amount
            payable_amount = record.payable_amount
            cash_amount = 0.0
            mfs_amount = 0.0
            card_amount = 0.0
            cash_paid = 0.0
            mfs_paid = 0.0
            card_paid = 0.0
        else:
            return

        # Calculate the refund amount based on the payable amount and adv values
        refund_amount = min(adv,paid, payable_amount)

        # Deduct the refund amount from the adv value
        if adv > 0:
            if cash_amount >= refund_amount:
                cash_amount -= refund_amount
            elif mfs_amount >= refund_amount - cash_amount:
                mfs_amount -= refund_amount - cash_amount
                cash_amount = 0
            else:
                card_amount -= refund_amount - cash_amount - mfs_amount
                mfs_amount = 0
                cash_amount = 0
            adv -= refund_amount
            # Update the due_amount and payable_amount values
            due_amount -= refund_amount
            payable_amount -= refund_amount
            # Set due_amount to 0 if it's negative
            due_amount = max(0, due_amount)
        elif paid > 0:
            if cash_paid >= refund_amount:
                cash_paid -= refund_amount
            elif mfs_paid >= refund_amount:
                mfs_paid -= refund_amount
            else:
                card_paid -= refund_amount - cash_paid - mfs_paid
                mfs_paid = 0
                cash_paid = 0
            paid -= refund_amount
            # Update the due_amount and payable_amount values
            due_amount -= refund_amount
            payable_amount -= refund_amount
            # Set due_amount to 0 if it's negative
            due_amount = max(0, due_amount)



        if active_model == 'admission.info':
            record.write({'adv': adv, 'due_amount': due_amount, 'payable_amount': payable_amount,
                          'cash_amount': cash_amount, 'mfs_amount': mfs_amount, 'card_amount': card_amount,
                          'cash_paid': cash_paid, 'mfs_paid': mfs_paid, 'card_paid': card_paid})
        elif active_model == 'bill.register':
            record.write({'adv': adv, 'due_amount': due_amount, 'payable_amount': payable_amount,
                          'cash_amount': cash_amount, 'mfs_amount': mfs_amount, 'card_amount': card_amount,
                          'cash_paid': cash_paid, 'mfs_paid': mfs_paid, 'card_paid': card_paid,})

        # # Generate reverse money receipt
        # money_receipt = self.env['money.receipt'].create({
        #     'date': fields.Date.today(),
        #     'bill_id': active_id if active_model == 'bill.register' else False,
        #     'admission_id': active_id if active_model == 'admission.info' else False,
        #     # 'paid': refund_amount,
        #     'adv': refund_amount,  # Update the adv field with the refund amount
        #     'due_amount': 0.0,
        #     'payment_type': 'refund',
        #     # Add other fields as needed
        # })
        #
        # # Generate reverse journal entry
        # journal_entry = self.env['journal.receipt'].create({
        #     'date': fields.Date.today(),
        #     'bill_id': active_id if active_model == 'bill.register' else False,
        #     'admission_id': active_id if active_model == 'admission.info' else False,
        #     # 'paid': refund_amount,
        #     'adv': refund_amount,  # Update the adv field with the refund amount
        #     'due_amount': refund_amount,
        #     'payment_type': 'refund',
        #     # Add other fields as needed
        # })


class PaymentInfoLineWizard(models.TransientModel): # Sub model data---
    _name = 'money.receipt.wizard.lines'

    date = fields.Datetime(string="DateTime")
    payment_process_type = fields.Selection([
        ('cash', 'Cash'),
        ('card', 'Card'),
        ('m_cash', 'MFS'),
        ('card_cash', 'Cash & Card'),
        ('m_cash_cash', 'Cash & MFS'),
        ('m_cash_card', 'MFS & Card'),
        ('card_cash_mcash', 'Cash, Card & MFS')
    ], default='cash')
    ac_no = fields.Char(string="Card A/C No.")
    psn = fields.Char(string="MFS Payment A/C")
    mcash_mobile_no_payment = fields.Char(string="M-Cash Mobile")
    card_amount = fields.Float(string="Card Amount")
    mfs_amount = fields.Float(string="MFS Amount")
    cash_amount = fields.Float(string="Cash Amount")
    card_no_payment = fields.Char(string="Card No.")
    reverse_mr_item_id = fields.Many2one('money.receipt.wizard', string="Payment Process Information")

    @api.model
    def default_get(self, fields_list):
        defaults = super(PaymentInfoLineWizard, self).default_get(fields_list)
        active_id = self._context.get('active_id')
        active_model = self._context.get('active_model')

        money_receipts = self.get_money_receipts(active_id, active_model)
        defaults['money.receipt'] = money_receipts.ids
        return defaults

    @property
    def _money_receipt_model(self):
        return self.env['money.receipt']

    def get_money_receipts(self, active_id, active_model):
        money_receipts = self._money_receipt_model.search([
            ('admission_id', '=', active_id if active_model == 'admission.info' else False),
            ('bill_id', '=', active_id if active_model == 'bill.register' else False)
        ])
        return money_receipts

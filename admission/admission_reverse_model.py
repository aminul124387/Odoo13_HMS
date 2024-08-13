from mock.mock import self

from odoo import fields, models, api
from odoo.addons.general_hospital_v_03.blood_bank.blood_bank import _
from odoo.exceptions import ValidationError


class AdmissionInfoWizard(models.TransientModel):
    _name = 'admission.info.wizard'

    date = fields.Datetime(string="Date", default=lambda self: fields.Datetime.now())
    admission_id = fields.Char(string='Admission ID', readonly=True)
    partner_id = fields.Many2one('res.users', 'Reversed By:', default=lambda self: self.env.user.id)

    admission_line_id = fields.One2many('admission.info.wizard.lines', 'admission_item_id')

    referred_by = fields.Many2one('doctors.profile', string="Referred By", domain=[('state', '=', 'active')])
    referral = fields.Many2one('broker.profile', "Referral", domain=[('state', '=', 'active')])
    operation_date = fields.Date(string='Operation Date')
    release_note = fields.Char(string="Release Note")

    discount_percent = fields.Float(string='Discount Percent (%)', default=0.0, digits='Discount')
    other_discount = fields.Float(string='Fixed Discount', default=0.0, digits='Discount')
    service_charge = fields.Integer(string='Service Charge')
    total_without_discount = fields.Float(string='Total Without Discount', compute='_onchange_total_amount')
    adv = fields.Float(string="Advance Payment")
    total = fields.Float(string='Grand Total', digits='Discount')
    paid = fields.Float(string='Paid Amount', tracking=True)
    due_amount = fields.Float("Due Amount", digits='Discount', default=0.0)
    payable_amount = fields.Float("Customer Payable Amount", default=0.0)
    refund_amount = fields.Float("Refund Amount", default=0.0)
    reverse_reason = fields.Text(string="Valid Reverse Reason:")
    discount_remarks = fields.Text(string='Discount Remarks')
    discount_required = fields.Boolean(compute='_compute_discount_required')


    def action_print_report_details(self):# Admission Details Report
        # admissions = self.env['admission.info'].search_read([])
        data = {
            'form_data': self.read([]),
            # 'admissions': admissions
        }
        return self.env.ref('general_hospital_v_03.details_report_admission_action').report_action(self, data = data)
    @api.depends('discount_percent', 'other_discount')  # This function is for the discount remarks field required!
    def _compute_discount_required(self):
        for record in self:
            record.discount_required = record.discount_percent != 0.0 or record.other_discount != 0.0

    @api.depends('admission_line_id.total_price', 'admission_line_id.sub_total_amount', 'payable_amount',
                 'other_discount', 'paid', 'refund_amount', 'due_amount')
    def _onchange_total_amount(self):
        self.total_without_discount = sum(line.total_price for line in self.admission_line_id)
        grand_total = sum(line.sub_total_amount for line in self.admission_line_id)

        # Add service charge to the grand total if applicable
        service_charge_total = sum(line.total_price * line.admission_item_id.service_charge / 100
                                   for line in self.admission_line_id
                                   if line.has_service_charge)

        self.total_without_discount += service_charge_total

        self.total = grand_total - self.other_discount
        self.due_amount = self.total - self.paid - self.adv

        if self.paid + self.adv > self.total: # To calculate the payable amount of the customer
            self.payable_amount = (self.paid + self.adv) - self.total
            if self.refund_amount:
                self.payable_amount -= self.refund_amount
                self.due_amount += self.refund_amount

        else:
            self.payable_amount = 0.0

    def admissionUpdateInfo(self): # This Function is Work to update data
        active_id = self._context.get('active_id') # Active id base data Find -----------
        # print("active_id", active_id)
        wizard_update=self.env['admission.info'].browse(active_id)
        # print("test data------", test_date)
        lst_item = []
        for rec in self.admission_line_id:
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
        wizard_update.admission_line_id = [(5,0,0)] # Exist bill item delete
        vals = {# Send item in the Dictionary
            'referral': self.referral.id,
            'referred_by': self.referred_by.id,
            'service_charge': self.service_charge,
            'discount_remarks': self.discount_remarks,
            'discount_percent': self.discount_percent,
            'other_discount': self.other_discount,
            'payable_amount': self.payable_amount,
            'refund_amount': self.refund_amount,
            'paid': self.paid,
            'total': self.total,
            'due_amount': self.due_amount,
            'admission_line_id': lst_item
        }
        wizard_update.write(vals)# Update Dictionary data in the bill.register Model
        if self.refund_amount > 0:
            jr_payment = self.env['journal.receipt'].create({  # Investigation data transfer to the Journal Receipt Model
                'refund_amount': self.refund_amount,
                'due_amount': self.due_amount,
                # 'admission_id': self.id,
                'payment_type': 'refund'
            })

            money_receipt = self.env['money.receipt'].create({
                'refund_amount': self.refund_amount,
                'due_amount': self.due_amount,
                # 'admission_id': self.id,
                'payment_type': 'refund'
            })
    @api.model
    def default_get(self, fields_list):
        defaults = super(AdmissionInfoWizard, self).default_get(fields_list)
        active_id = self._context.get('active_id')
        adm_data = self.env['admission.info'].browse(active_id)

        field_mappings = {
            'admission_id': 'admission_id',
            'discount_remarks': 'discount_remarks',
            'discount_percent': 'discount_percent',
            'other_discount': 'other_discount',
            'service_charge': 'service_charge',
            'refund_amount': 'refund_amount',
            'payable_amount': 'payable_amount',
            'paid': 'paid',
            'adv': 'adv',
            'total': 'total',
            'due_amount': 'due_amount',
        }

        if 'referred_by' in fields_list:
            defaults['referred_by'] = adm_data.referred_by.id if adm_data.referred_by else False

        if 'referral' in fields_list:
            defaults['referral'] = adm_data.referral.id if adm_data.referral else False


        for field in field_mappings.keys():
            if field in fields_list:
                defaults[field] = getattr(adm_data, field_mappings[field])

        if 'admission_line_id' in fields_list:
            line_defaults = []
            for line in adm_data.admission_line_id:
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
            defaults['admission_line_id'] = line_defaults
        return defaults


class AdmissionInfoLineWizard(models.TransientModel):
    _name = 'admission.info.wizard.lines'

    department = fields.Many2one(string='Department', related='item_name.department')
    price = fields.Float(string='Price', related='item_name.price')
    total_price = fields.Float(string='Price', compute='onchange_subtotal_amount')
    quantity = fields.Integer("Quantity", default=1)
    # discount = fields.Integer(string='Discount')
    discount_percent = fields.Float(string='Discount (%)', related='admission_item_id.discount_percent')
    flat_discount = fields.Float(string='Flat Discount', related='admission_item_id.other_discount')
    total_discount = fields.Float(string='Total Discount')
    sub_total_amount = fields.Float(string='Total Amount')
    # -------------------------------- Relation change please---------
    item_name = fields.Many2one("item.entry", "Item", ondelete='cascade')
    admission_item_id = fields.Many2one('admission.info.wizard', "Information")
    has_service_charge = fields.Boolean(string='Service Charge(%)', related='item_name.has_service_charge')

    @api.depends('price', 'quantity', 'discount_percent', 'admission_item_id.service_charge', 'has_service_charge')
    def onchange_subtotal_amount(self):
        for record in self:
            record.total_price = record.price * record.quantity
            record.total_discount = (record.total_price * record.discount_percent) / 100
            record.sub_total_amount = record.total_price - record.total_discount

            if record.has_service_charge:
                service_charge_percent = record.admission_item_id.service_charge or 0.0
                service_charge_amount = (record.sub_total_amount * service_charge_percent) / 100
                record.sub_total_amount += service_charge_amount

            if record.quantity < 0:
                raise ValidationError('Your Product Quantity cannot be negative!')
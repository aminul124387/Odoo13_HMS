import base64
from io import BytesIO
from gevent.subprocess import value
from odoo import fields, models, api
from odoo.exceptions import UserError
from datetime import datetime, timedelta
from odoo.tools import html_escape
from odoo.exceptions import ValidationError
from odoo import exceptions



class AdmissionInfo(models.Model):
    _name = 'admission.info'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'admission_id'
    _order = 'admission_id desc'

    date = fields.Datetime(string="Date", default=lambda self: fields.Datetime.now())
    admission_id = fields.Char(string='Admission ID', readonly=True)

    patient_id = fields.Many2one(string='Patient ID',readonly=True)
    # ------------------ Patient Table Relation
    patient_name = fields.Many2one('patient.info', string="Patient Name", tracking=True)
    # ------------------ Admission Bill Relation
    # admission_line_id = fields.One2many('admission.info.line', 'admission_item_id')
    # ---------------------- Guarantor Relation
    guarantor_line_id = fields.One2many('admission.guarantor.line', 'guarantor_item_id')
    # --------------------- Payment Relation
    hospital_admission_payment_line = fields.One2many('hospital_admission.payment.line', 'payment_item_id', 'Payment Info')
    # --------------------- Journal Relati                                                                                           on
    admission_journal_line_id = fields.One2many('admission.billjournal.line', 'admission_journal_item_id', 'Journal Info')

    address = fields.Char(string='Address', related="patient_name.address")
    age = fields.Char(string="Age", related="patient_name.age")
    gender = fields.Selection(related='patient_name.gender')
    blood_group = fields.Selection(string='Blood Group', related="patient_name.blood_group")
    email = fields.Char(string='Email', related='patient_name.email')
    mobile = fields.Char(string='Mobile', related='patient_name.mobile')
    # referel_name = fields.Many2one('broker.profile', "Broker Name")

    # ---------------- Dr. Reffered Relation ----------------------
    referred_by = fields.Many2one('doctors.profile', string="Referred By", domain=[('state', '=', 'active')])
    referral = fields.Many2one('broker.profile', "Referral", domain=[('state', '=', 'active')])
    operation_date = fields.Date(string='Operation Date')
    # service_charge = fields.Integer(string="Service Charge(%)")
    emergency_dept = fields.Boolean(string="Emergency Dept.")
    state = fields.Selection([('release', 'Release'),
                              ('created', 'Created'),
                              ('pending', 'Pending'),
                              ('confirmed', 'Confirmed'),
                              ('paid', 'Paid'),
                              ('cancelled', 'Cancelled')], 'State', default='pending',
                             readonly=True, required=True)



    # --------------------------------Payment Type Rlation -------------------------------------------------------------

    # Payement wise Field start Here -------------------
    payment_type = fields.Selection([('cash', 'Cash'),
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
    card_amount = fields.Float("Card Amount")
    card_paid = fields.Float("Card Amount")
    mfs_amount = fields.Float("MFS Amount")
    mfs_paid = fields.Float("MFS Amount")
    cash_amount = fields.Float("Cash Amount")
    cash_paid = fields.Float("Cash Amount")
    card_no_payment = fields.Char(string="Card Number",
                                  attrs={'invisible': [('payment_type', '!=', 'card')]})
    # ------------------------------------------------------------------------------------------

    service_charge = fields.Float(string='Admission Service Charge(%)', placeholder='Service Charge (%)')

    discount_percent = fields.Float(string='Discount Percent (%)', default=0.0, digits='Discount')
    other_discount = fields.Float(string='Fixed Discount', default=0.0, digits='Discount')
    discount_amount = fields.Float(string='Discount Amount',default=0.0, digits='Discount')
    discount_remarks = fields.Text(string='Discount Remarks')
    discount_required = fields.Boolean(compute='_compute_discount_required')


    currency_id = fields.Many2one('res.currency', string="Currency",
                                  default=lambda self: self.env['res.currency'].search([('name', '=', 'BDT')]))
    total_without_discount = fields.Float(string='Total Without Discount', compute='_onchange_total_amount')
    total = fields.Float(string='Grand Total', digits='Discount')
    paid = fields.Float(string='Paid Amount', tracking=True)
    adv = fields.Float(string="Advance Payment")
    due_amount = fields.Float("Due Amount", digits='Discount', default=0.0)
    payable_amount = fields.Float("Customer Payable Amount", default=0.0, compute='_onchange_total_amount')
    refund_amount = fields.Float("Refund Amount", default=0.0)
    bill_payments = fields.One2many('bill.bill_pay', 'bill_id', string='Payments')
    #----
    cancel_ids = fields.One2many('cancel.appointment', 'cancel_adn_id', string='Cancellation Records')
    # approved_by = fields.Char(string="Cancel Approved By:")
    cancel_reason = fields.Text(string="Cancel Reason")
    cancel_date = fields.Datetime(string='Cancel Date')
    release_note = fields.Text(string="Release Note")
    treatment = fields.Text(string="Hospital Treatment")
    diagnosis = fields.Char(string="Patient Diagnosis")
    release_note_date = fields.Datetime(string='Release Time')
    release_note_make_by = fields.Many2one('res.users', 'Released By')
    cancel_approved_by = fields.Char('Approved By')
    user_id = fields.Many2one('res.users', 'Current User', default=lambda self: self.env.user.id)

    def btn_investigation_item_pos(self):
        print("This Investigation is testing for Admission!")
        # default_lines = []
        # items = self.env['pos.order'].search()

    def btn_release_slip_print(self):# Admission Release slip Button
        return self.env.ref('general_hospital_v_03.report_admission_info_release_template_action_id').report_action(self)
    def action_open_release_note_popup(self):# This Function is used to Release Button------
        if self.release_note:
            raise ValidationError("This Admission is Already Noted!")
        view_id = self.env.ref('general_hospital_v_03.release_note_popup_view_form').id
        return {
            'name': 'Release Note',
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'release.note',
            'views': [(view_id, 'form')],
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {'default_admission_id': self.id},
        }

    @api.depends('discount_percent', 'other_discount')# This function is for the discount remarks field required!
    def _compute_discount_required(self):
        for record in self:
            record.discount_required = record.discount_percent != 0.0 or record.other_discount != 0.0
    @api.model
    def default_admission_line_ids(self): # This function is used to auto field set into the Admission line item
        # Create default admission line items
        default_lines = []
        items = self.env['item.entry'].search([('has_auto_select_admission', '=', True)]) # Item check for auto selection
        for item in items:
            has_service_charge = item.has_service_charge if item.has_service_charge else False
            more_than_one_days = item.more_than_one_days if item.more_than_one_days else False

            line_values = {
                'item_name': item.id,
                'quantity': 1,
                'has_service_charge': has_service_charge,
                'more_than_one_days': more_than_one_days,
                'has_auto_select_admission': True,
            }
            default_lines.append((0, 0, line_values))
        return default_lines

    admission_line_id = fields.One2many('admission.info.line', 'admission_item_id', default=default_admission_line_ids)

    def btn_cancel_form_show(self):  # This function start to cancell form show ------
        if self.state == 'cancelled':
            raise ValidationError("This Bill is already Cancelled!")
        elif self.state=='release':
            raise ValidationError("Release Admission Cannot be Cancel From the Application!")
        elif self.state=='paid':
            raise ValidationError("Please Contact the Administrator This Admission is already Paid!")
        ir_model_data = self.env['ir.model.data']
        template_id = ir_model_data.get_object_reference('general_hospital_v_03', 'view_cancel_model_form')[1]
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_id': template_id,
            'res_model': 'cancel.appointment',
            'target': 'new',
            'context': {
                'default_cancel_model_type': 'admission',
                'default_cancel_adn_id': self.id,
                # 'default_cancel_date': self.id,
            }
        }

    def cancel(self):# This function is use for the Admission form Cancel
        if self.state == 'cancelled':
            raise exceptions.UserError('This form is already cancelled.')
        elif self.due_amount == 0:
            if not self.cancel_reason:
                raise exceptions.UserError('Give the valid Cancel Reason')

        # Cancel all related money receipts
        money_receipts = self.env['money.receipt'].search([('admission_id', '=', self.id)])
        money_receipts.filtered(lambda r: r.state != 'cancelled').write({'state': 'cancelled'})
        journal_receipts = self.env['journal.receipt'].search([('admission_id', '=', self.id)])
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
        return True # Cancel button Function is end here

    def action_confirm_bill(self):# This function is used for Add Payment Button
        if self.state == 'confirmed':
            raise ValidationError("Admission is already confirmed!")
        elif self.state == 'release':
            raise ValidationError("This Admission cannot be confirmed!")
        elif self.state == 'paid':
            raise ValidationError("This Admission Already Paid!")
        elif self.state == 'cancelled':
            raise ValidationError('This Admission is Cancelled it cannot be Confirmed')
        self.state = 'confirmed'
        if self.adv > 0:
            money_receipt = self.env['money.receipt'].create({  # Investigation data transfer to the Money Receipt Model
                'date': self.date,
                'admission_id': self.id,
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
                'payment_item_id': self.id  # link to the bill record
            }
            self.env['hospital_admission.payment.line'].create(payment_vals)
        jr_payment = self.env['journal.receipt'].create({  # Investigation data transfer to the Journal Receipt Model
            'date': self.date,
            'admission_id': self.id,
            'total': self.total,
            'adv': self.adv,
            'due_amount': self.due_amount,
            'payment_type': 'adv'
        })
        jr_payment_vals = {
            'journal_id': jr_payment.id,
            'admission_journal_item_id': self.id  # link to the bill record
        }
        self.env['admission.billjournal.line'].create(jr_payment_vals)
        # Save changes to the database
        self.env.cr.commit()
        return self.env.ref('general_hospital_v_03.report_admission_action_form').report_action(self)

    def add_payment_btn(self):# This Function is use for the add payment options
        if self.state == 'pending':
            raise ValidationError("First Confirm the Bill")
        elif self.state == 'release':
            raise ValidationError("The Admission is already Paid")
        ir_model_data = self.env['ir.model.data']
        template_id = ir_model_data.get_object_reference('general_hospital_v_03', 'bill_pay_form_view')[1]
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_id': template_id,
            'res_model': 'bill.bill_pay',
            'target': 'new',
            'context':{
                'default_admission_id':self.id,
                'default_amount':self.due_amount
            }

        }


    def btn_release_check_due_amount(self):# This Function is used to release button action
        for admission in self:
            if admission.due_amount > 0 or admission.due_amount < 0 or self.state == 'pending' or not self.release_note:
                raise exceptions.UserError("** Please Check Due Amount or Release Note ! **")
            admission.write({'state': 'release'})
        return True

    @api.model # This function used to Create the Admission ID Generate
    def create(self, vals):
        record = super().create(vals)
        if record:
            name_text_admission = 'A-0100' + str(record.id)
            record.update({'admission_id': name_text_admission, 'state': 'pending'})
        return record
    @api.onchange('paid', 'other_discount', 'discount_percent') # This Function used to Field Validation
    def check_due_amount(self):
        for record in self:
            # if record.paid or record.other_discount or record.discount_percent or record.total_without_discount or record.due_amount or record.total and not re.match("^[a-zA-Z0-9]+$", record.my_field):
            #     raise ValidationError("Field can only contain alphanumeric characters")
            if record.discount_percent < 0:
                raise ValidationError("Discount Percent Field cannot be negative")
            # elif record.due_amount < 0:
            #     raise ValidationError("Due amount cannot be negative")
            elif record.paid < 0:
                raise self.ValidationError("Paid Value Cannot be Negative")
            elif record.total < 0:
                raise self.ValidationError("Grand Total Cannot ne Negative")
            # Doctor Discount and Discount Percent Validation is on the below:
            elif self.referred_by and self.discount_percent >= 31 or self.discount_percent > 80 or self.discount_percent < 0:
                raise ValidationError("Give 80% or less Discount OR Cannot provide 30% up Doctor Discount, Please remove Minus value")


# -------  Item Based Calculation Function is end Here -------  ------------------  --------------
    @api.depends('admission_line_id.total_price', 'admission_line_id.sub_total_amount', 'payable_amount',
                 'other_discount', 'paid', 'card_amount', 'mfs_amount', 'cash_amount', 'refund_amount')
    def _onchange_total_amount(self):
        self.total_without_discount = sum(line.total_price for line in self.admission_line_id)
        grand_total = sum(line.sub_total_amount for line in self.admission_line_id)

        # Add service charge to the grand total if applicable
        service_charge_total = sum(line.total_price * line.admission_item_id.service_charge / 100
                                   for line in self.admission_line_id
                                   if line.has_service_charge)
        self.total_without_discount += service_charge_total

        self.total = grand_total - self.other_discount
        self.adv = self.card_amount + self.mfs_amount + self.cash_amount
        self.due_amount = self.total - self.paid - self.adv
        # Payable amount onchange calculate
        total_paid = self.paid + self.adv
        if total_paid > self.total: # To calculate the payable amount of the customer
            self.payable_amount = total_paid - self.total
            if self.refund_amount:
                self.payable_amount -= self.refund_amount
                self.due_amount += self.refund_amount
        else:
            self.payable_amount = 0.0




# --------------------------------------------------  Note book menu Iten code ----------------
# =============================================================================================
class AdmissionLineInfo(models.Model):
    _name = 'admission.info.line'

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
    admission_item_id = fields.Many2one('admission.info', "Information")
    sequence = fields.Integer(string='Seq')
    service_charge = fields.Float(string="service charge(%)")
    has_auto_select_admission = fields.Boolean(string='Item Auto Select Field(Admission)')
    has_service_charge = fields.Boolean(string='Service Charge(%)', related='item_name.has_service_charge')
    more_than_one_days = fields.Boolean(string='Days')
    createdate = fields.Datetime(string="Date", related='admission_item_id.date')

    # @api.depends('price', 'quantity', 'discount_percent', 'admission_item_id.service_charge', 'has_service_charge')
    # def onchange_subtotal_amount(self):
    #     for record in self:
    #         record.total_price = record.price * record.quantity
    #         record.total_discount = (record.total_price * record.discount_percent) / 100
    #         record.sub_total_amount = record.total_price - record.total_discount
    #
    #         if record.has_service_charge:
    #             service_charge_percent = record.admission_item_id.service_charge or 0.0
    #             service_charge_amount = (record.sub_total_amount * service_charge_percent) / 100
    #             record.sub_total_amount += service_charge_amount
    #
    #         if record.quantity < 0:
    #             raise ValidationError('Your Product Quantity cannot be negative!')

    @api.depends('price', 'quantity', 'discount_percent', 'admission_item_id.service_charge', 'has_service_charge',
                 'more_than_one_days', 'createdate')
    def onchange_subtotal_amount(self):
        for record in self:
            if record.quantity < 0:
                raise ValidationError('Your Product Quantity cannot be negative!')

            # Calculate the total price and total discount based on the updated quantity
            record.total_price = record.price * record.quantity
            record.total_discount = (record.total_price * record.discount_percent) / 100

            # Calculate the sub total amount based on the total price and total discount
            record.sub_total_amount = record.total_price - record.total_discount

            if record.has_service_charge:
                service_charge_percent = record.admission_item_id.service_charge or 0.0
                service_charge_amount = (record.sub_total_amount * service_charge_percent) / 100
                record.sub_total_amount += service_charge_amount

            # Check if the item has more_than_one_days and if 1 hour has passed since the created date
            if record.more_than_one_days:
                if record.createdate and record.createdate + timedelta(hours=1) <= datetime.now():
                    if record.quantity == 1:
                        record.quantity = 2

                    # Recalculate the total price and total discount based on the updated quantity
                    record.total_price = record.price * record.quantity
                    record.total_discount = (record.total_price * record.discount_percent) / 100

                    # Recalculate the Sub Total amount based on the total price and total discount
                    record.sub_total_amount = record.total_price - record.total_discount

                    if record.has_service_charge:
                        service_charge_percent = record.admission_item_id.service_charge or 0.0
                        service_charge_amount = (record.sub_total_amount * service_charge_percent) / 100
                        record.sub_total_amount += service_charge_amount


# -================================================= admission_payment_line_id ==============================
class HospitalAdmissionPaymentLine(models.Model):
    _name = 'hospital_admission.payment.line'

    admission_bill_pay_id = fields.Many2one('bill.bill_pay', string='Bill Payment')
    money_receipt_id = fields.Many2one('money.receipt', string='Money Receipt')
    date = fields.Datetime(string='Payment Date')
    paid = fields.Float(string='Payment Amount')
    adv = fields.Float(string='Advance')
    cash_amount = fields.Float("Cash Amount")
    cash_paid = fields.Float("Cash Amount")
    ac_no = fields.Char("Card A/C No.")
    psn = fields.Char(string="MFS Payment A/C")
    mcash_mobile_no_payment = fields.Char(string="M-Cash Mobile")
    card_amount = fields.Float("Card Amount")
    card_paid = fields.Float("Card Amount")
    mfs_amount = fields.Float("MFS Amount")
    mfs_paid = fields.Float("MFS Amount")
    payment_type = fields.Char(string='Payment Type')
    card_no_payment = fields.Char(string='Card No.')
    user_id = fields.Many2one('res.users', 'Current User', default=lambda self: self.env.user.id)
    payment_item_id = fields.Many2one("admission.info", "Information")
    due_amount = fields.Float("Due Amount", digits='Discount', default=0.0)
class AdmissionJournalLine(models.Model):
    _name = 'admission.billjournal.line'

    journal_id = fields.Many2one('journal.receipt', string="Journal ID")
    # bill_admission_pay_jr_id = fields.Many2one('bill.bill_pay', string='Bill Payment') # This field is not use able
    admission_pay_jr_ids = fields.Many2one('bill.bill_pay', string='Bill Payment')
    admission_journal_item_id = fields.Many2one("admission.info", "Information")
# --========================================== Guarantor Line  Code ===================================
class AdmissionGuarantorLineId(models.Model):
    _name = 'admission.guarantor.line'

    # ------------------------------------- Guarantor Item Relationship ---------------------
    guarantor_name = fields.Many2one("guarantor.profile", "Guarantor Name", ondelete='cascade')
    guarantor_item_id = fields.Many2one("admission.info", "Information")
    # ----------------------------------------------------------------------------
    guarantor_address = fields.Char(string='Address Details', related='guarantor_name.guarantor_address')
    guarantor_relationship = fields.Char(string='Relationship', related='guarantor_name.guarantor_relationship')
    guarantor_contact = fields.Char(string='Contact Details', related='guarantor_name.guarantor_contact')

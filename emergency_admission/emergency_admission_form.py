from odoo import fields, models, api
from odoo.exceptions import UserError


# <field name="name" string="Name" filter_domain="['|',('name','ilike',self),('id','ilike',self)]"/>

class EmergencyAdmissionInfo(models.Model):
    _name = 'emergency_admissin.info'
    _rec_name = 'emergency_admission_id'
    _order = "emergency_admission_id desc"

    date = fields.Datetime(string="Date of Birth", default=lambda self: fields.Datetime.now())
    emergency_admission_id = fields.Char(string='Emergency Admission ID', readonly=True)

    patient_id = fields.Char(string='Patient ID', related='patient_name.patient_id', readonly=True)
    # ------------------ Patient Table Relation
    patient_name = fields.Many2one('patient.info', string="Patient Name")
    # ------------------ Admission Bill Relation
    emergency_admission_line_id = fields.One2many('emergency_admissin.info.line', 'admission_item_id', required=True)
    # ---------------------- Guarantor Relation
    emergency_guarantor_line_id = fields.One2many('emergency.admission.guarantor.line', 'guarantor_item_id')
    # --------------------- Payment Relation
    emergency_admission_payment_line_id = fields.One2many('admission.payment.line', 'payment_item_id')
    # --------------------- Journal Relation
    emergency_admission_journal_relation_line_id = fields.One2many('admission.journal.line', 'admission_journal_item_id')

    address = fields.Char(string='Address', related="patient_name.address")
    age = fields.Char(string="Age", related="patient_name.age")
    gender = fields.Selection(related='patient_name.gender', store=True)

    email = fields.Char(string='Email', related='patient_name.email')
    mobile = fields.Char(string='Mobile', related='patient_name.mobile')

    # ---------------- Dr. Reffered Relation ----------------------
    referred_by = fields.Many2one('doctors.profile', string="Referred By", domain=[('status', '=', 'active')])
    operation_date = fields.Date(string='Operation Date')
    package = fields.Many2one('package.info', string="Admission Package")
    emergency_dept = fields.Boolean(string="Emergency Dept.")
    release_note = fields.Char(string="Release Note", readonly=True)
    state = fields.Selection([('created', 'Created'),
                              ('pending', 'Pending'),
                              ('confirmed', 'Confirmed'),
                              ('cancelled', 'Cancelled')], 'Status', default='pending',
                             readonly=True)

    # --------------------------------Payment Type Rlation --------------------------------------------------------------
    admission_payment_type = fields.Many2one('payment.type', string='Payment Type')

    account_number = fields.Char(string='Account Number')
    total_without_discount = fields.Float(string='Total Without Discount')
    discount_percent = fields.Float(string='Discount Percent (%)')
    other_discount = fields.Float(string='Other Discount')
    total = fields.Float(string='Total')
    grand_total = fields.Float(string='Grand Total')
    paid_amount = fields.Float(string='Paid Amount')
    service_charge = fields.Float(string='Service Charge')
    due_amount = fields.Float(string='Due Amount')

    # -----------------------------------------------------------
    # @api.multi
    # def name_get(self):
    #     res = []
    #     for rec in self:
    #         res.append((rec.id, '%s - %s' % (rec.name_seq, rec.patient_name)) )
    # This Function is used for the id generate for Patient field -------------------------------
    #     @api.model
    #     def _name_search(self, patient_name, args=None, operator='ilike', limit=100, name_get_uid=None):
    #         args == args or []
    #         domain = []
    #         if patient_name:
    #             domain = ['|','|', ('patient_id', operator.patient_name), ('patient_name', operator.patient_name),('mobile', operator.patient_name)]
    #         return self. _search(domain + args, limit=limit, access_right_uid =name_get_uid)
    #
    # @api.model_create_multi
    # def print_quotation_report(self):
    #     return self.env.ref('hospital_Multiple_form.report_ModelName_id').report_action(self)

    # def print_report(self):
    #     data = {
    #         'emergency_admissin.info': self.id,
    #     }
    #
    #     return self.env.ref('emergency_admissin.info.print_report_pdf').report_action(self, data=data)

    # import pdb
    # pdb.set_trace()
    # This Fuction is used for the Cancel Button ===========================
    # def action_cancel(self):
    #     self.ensure_one()
    #     self.state = 'cancelled'

    def action_confirm(self):
        self.ensure_one()
        if self.state == 'cancelled':
            raise UserError("Cannot Confirmed a cancelled admission.")
        self.state = 'confirmed'
    def action_cancel(self):
        self.ensure_one()
        # if self.state == 'confirmed':
        #     raise UserError("Cannot Cancel a Confirmed admission.")
        self.state = 'cancelled'
        # This Function is used for Patient ID Generate ==============================

    @api.model
    def create(self, vals):
        record = super().create(vals)
        if record:
            name_text_admission = 'EA-0100' + str(record.id)
            record.update({'emergency_admission_id': name_text_admission, 'state': 'created'})
        return record


# --------------------------------------------------  Note book menu Iten code ----------------
# =============================================================================================
class EmergencyAdmissionLineInfo(models.Model):
    _name = 'emergency_admissin.info.line'

    department = fields.Many2one(string='Department', related='item_name.department')
    price = fields.Float(string='Price', related='item_name.price')
    discount = fields.Float(string='Discount')
    discount_percent = fields.Float(string='Discount (%)')
    flat_discount = fields.Float(string='Flat Discount')
    total_discount = fields.Float(string='Total Discount')
    total_amount = fields.Float(string='Total Amount')
    # -------------------------------- Relation change please---------
    item_name = fields.Many2one("item.entry", "Item Name", ondelete='cascade')
    admission_item_id = fields.Many2one('emergency_admissin.info', "Information")


# --========================================== Guarantor Line  Code ===================================
class Emergency_Admission_guarantor_line_id(models.Model):
    _name = 'emergency.admission.guarantor.line'

    # ------------------------------------- Guarantor Item Relationship ---------------------
    guarantor_name = fields.Many2one("guarantor.profile", "Guarantor Name", ondelete='cascade')
    guarantor_item_id = fields.Many2one("emergency_admissin.info", "Information")
    # ----------------------------------------------------------------------------
    guarantor_address = fields.Char(string='Address Details', related='guarantor_name.guarantor_address')
    guarantor_relationship = fields.Char(string='Relationship', related='guarantor_name.guarantor_relationship')
    guarantor_contact = fields.Char(string='Contact Details', related='guarantor_name.guarantor_contact')


# -================================================= admission_payment_line_id ==============================

class EmergencyAdmissionAdmissionPaymentLineId(models.Model):
    _name = 'admission.payment.line'

    payment_date = fields.Char(string='Payment Date')
    payment_amount = fields.Float(string='Payment Amount')
    payment_type = fields.Char(string='Payment Type')
    card_no = fields.Char(string='Card No.')
    bank_name = fields.Many2one("payment.type", "Bank Name", ondelete='cascade')
    payment_item_id = fields.Many2one("emergency_admissin.info", "Information")
    money_receipt_id = fields.Char(string='Money Receipt ID')


# =====================================  admission_journal_relation_id ===============================
class EmergencyAdmissionJournalRelationLineId(models.Model):
    _name = 'admission.journal.line'

    journal_id = fields.Many2one("admission.journal.line", "Journal ID", ondelete='cascade')
    admission_journal_item_id = fields.Many2one("emergency_admissin.info", "Information")

import base64
from datetime import datetime, date
from odoo.modules import get_module_resource
from odoo import fields, models, api



class PatientInfo(models.Model):
    _name = 'prescriptions.info'
    _rec_name = 'prescriptions_id'


    prescriptions_id = fields.Char(string='Prescription ID', readonly=True)
    name = fields.Many2one('patient.info', string='Patient Name')
    pharmacy = fields.Char(string='Pharmacy')
    date = fields.Datetime(string='Time')






    state = fields.Selection([
        ('created', 'Created'),
        ('consultancy_invoice', 'Consultancy Invoice'),
        ('create_invoice', 'Create Invoice'),
        ('print_prescription', 'Print Prescription'),
        ('send_to_pharmacy', 'Send Pharmacy'),
        ('draft', 'Draft'),
        ('cancelled', 'Cancelled')], 'Status', default='draft', readonly=True)

    # ------------------ Admission Line Item Relation --------------------------------------------
    prescriptions_line_id = fields.One2many('prescriptions.info.line', 'prescriptions_item_id', required=True)
    # ----------------------------------------------------------------------------------------------

    total = fields.Float(string='Total')
    grand_total = fields.Float(string='Grand Total')
    paid_amount = fields.Float(string='Paid Amount')
    due_amount = fields.Float(string='Due Amount')

    # consultancy_invoice_count = fields.Integer()
    # # appointment_count = fields.Integer(string='Appointment Count')
    # appointment_count = fields.Integer(string='Appointment Count')


    # This Fuction is used for the Cancel Button =========================== item_cancel
    def Customer_Cancel(self):
        self.ensure_one()
        self.state = 'cancelled'

    def Customer_Invoice(self):
        self.ensure_one()
        self.state = 'create_invoice'

    def Consultancy_Invoice(self):
        self.ensure_one()
        self.state = 'consultancy_invoice'
    def Medicine_send_Pharmacy(self):
        self.ensure_one()
        self.state = 'send_to_pharmacy'
    def Print_Prescription(self):
        self.ensure_one()
        self.state = 'print_prescription'

    # @api.depends('dob')
    # def _compute_age(self):
    #     for record in self:
    #         if record.dob:
    #             today = datetime.datetime.now().date()
    #             age = today.year - record.dob.year - ((today.month, today.day) < (record.dob.month, record.dob.day))
    #             record.age = age

    # This Function is used for Patient ID Generate

    @api.model
    def create(self, vals):
        record = super().create(vals)
        if record:
            name_text = 'Prs-010' + str(record.id)
            record.update({'prescriptions_id': name_text,'state': 'created'})
        return record

        # This Function is used for the field Name show with the Customer ID Generate

    # @api.model
    # def name_get(self):
    #     res = []
    #     for record in self:
    #         patient_name = record.name
    #         prescriptions_id = record.prescriptions_id or '--'
    #         res.append((record.id, f"{patient_name} {' '} {prescriptions_id}"))
    #     return res

    # ------------ This function is used for data retrieve --------------
    # @api.model
    # def write(self, vals):
    #     change_patient = self
    #     if "age" in vals:
    #         newage = vals['age']
    #
    #     return super(PatientInfo, self).write(vals)





# --------------------------------------------------  Note book menu Iten code ----------------
# =============================================================================================
class PrescriptionsLineInfo(models.Model):
    _name = 'prescriptions.info.line'

    department = fields.Many2one(string='Department', related='item_name.department')
    price = fields.Float(string='Price', related='item_name.price')
    total_amount = fields.Float(string='Total Amount', related='item_name.total_amount')
    # -------------------------------- Relation change please---------
    item_name = fields.Many2one("item.entry", "Item Name", ondelete='cascade')
    prescriptions_item_id = fields.Many2one('prescriptions.info', "Information")

    # -------------------------------   This part is used for the onchange value item of notebook -----------------------------

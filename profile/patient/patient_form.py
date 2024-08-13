import base64
import string
import barcode
import xlwt
from io import BytesIO
from barcode.writer import ImageWriter
from datetime import datetime, date
from odoo.modules import get_module_resource
from odoo import fields, models, api
from odoo.addons.general_hospital_v_03.blood_bank.blood_bank import _
from odoo.exceptions import ValidationError


class PatientInfo(models.Model):
    _name = 'patient.info'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'patient_id desc'
    # _inherit = ['mail.thread']

    user_id = fields.Many2one('res.users', 'Created By:', default=lambda self: self.env.user.id)
    patient_id = fields.Char(string='Patient ID', readonly=True)
    photo = fields.Binary(string='Photo')
    name = fields.Char(string='Patient Name', tracking=True, required=True, index=True)
    mobile = fields.Char(string='Mobile', tracking=True)
    barcode = fields.Char(string='Barcode')
    email = fields.Char(string='Email')
    blood_group = fields.Selection([
        ('a+', 'A+')
        , ('a-', 'A-')
        , ('b+', 'B+')
        , ('b-', 'B-')
        , ('ab+', 'AB+')
        , ('ab+', 'AB-')
        , ('o+', 'O+')
        , ('none', 'None')
        , ('o-', 'O-')], 'Blood Group', default='none')
    marital_status = fields.Selection([
        ('married', 'Married'),
        ('single', 'Single'),
        ('none', 'None')
    ], 'Marital Status', default='none')
    parent_name = fields.Char(string='Parent Name')
    partner_name = fields.Char(string='Partner Name')
    rh = fields.Char(string='RH')
    family_physician = fields.Many2one('doctors.profile', string='Family Physician')
    doctor_uid =fields.Many2one('res.users', string='Select Doctor')
    address = fields.Char(string='Address')
    date_of_birth = fields.Date(string='Date Of Birth')
    age = fields.Char(string='Age')
    is_company = fields.Boolean(string='Is a Company?', default=True)
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ], default='male')

    state = fields.Selection([
        ('created', 'Created'),
        ('confirmed', 'Confirmed'),
        ('draft', 'Draft'),
        ('cancelled', 'Cancelled')], 'Status', default='draft', readonly=True)

    # ------------------ Admission Line Item Relation --------------------------------------------
    patient_line_id = fields.One2many('patient.info.line', 'patient_item_id', required=True)
    # ----------------------------------------------------------------------------------------------
    total = fields.Char(string='Total')
    grand_total = fields.Char(string='Grand Total')
    paid_amount = fields.Char(string='Paid Amount')

    admission_info = fields.One2many('admission.info', 'patient_name', "Bill Register",
                                     domain=[('state', '=', 'confirmed')])
    admission_count = fields.Integer(string='Admission', compute='count_admission')
    bill_info =fields.One2many('bill.register','patient_name', "Bill Register", domain=[('state', '=', 'confirmed')])
    bill_count = fields.Integer(string='Investigation', compute='count_bills')
    appointment_info = fields.One2many('appointment.booking', 'patient_name', 'Appointment', domain=[('state', '=', 'reached')])
    appointment_count = fields.Integer(string='Appointment', compute='count_appointment')
    evaluation_count = fields.Integer(string='Evaluation Count')

    # This Function is used to the Name, Mobile Number and email Searching Patient Name -------------------------------------
    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100):
        if args is None:
            args = []
        domain = args + ['|', '|', '|', ('patient_id', operator, name), ('name', operator, name),('mobile', operator, name),('email', operator, name)]
        return super(PatientInfo, self).search(domain, limit=limit).name_get()



    @api.depends('appointment_info')
    def count_appointment(self):
        for record in self:
            count = self.env['appointment.booking'].search_count([('patient_name', '=', record.id)])
            record.appointment_count = count

    def button_patient_card_send_by_email(self):# This function is use to send the email button function to the user
        template_id = self.env.ref('general_hospital_v_03.patient_card_email_template')
        template = self.env['mail.template'].browse(template_id.id)
        template.send_mail(self.id,force_send=True)

        for patient in self:
            template.send_mail(patient.id, force_send=True)
    @api.depends('admission_info')# This fucntion use to admission count in patien form
    def count_admission(self):
        self.admission_count = len(self.admission_info)


    def unlink(self):# This Function is used for the Bill Delete Validation Error!
        for record in self:
            if self.appointment_info or self.admission_info or self.bill_info:
                raise ValidationError("You cannot delete this, it has Admission or Appointment or Investigation!")
        try:
            return super(PatientInfo, self).unlink()
        except Exception as e:
            raise ValidationError(_("Something went wrong during the deletion: %s") % str(e))


    @api.depends('bill_info')# This function is use for the Investigation Count as per patient.
    def count_bills(self):
        self.bill_count = len(self.bill_info)

    # This Fuction is used for the name first letter capital  ===----------------------------
    @api.onchange('name')
    def onchange_name(self):
        self.name = string.capwords(self.name) if self.name else None
    # This Fuction is used Patient Image Show ===----------------------------
    @api.model # This function is used for the profile image...
    def _default_image(self):
        ''' --- Method to get default Image --- '''
        image_path = get_module_resource('hr', 'static/src/img',
                                         'default_image.png')
        return base64.b64encode(open(image_path, 'rb').read())


    # This Fuction is used for the Cancel Button =========================== item_cancel
    def customer_cancel(self):# this function is use for the cancel button.
        self.ensure_one()
        self.state = 'cancelled'

    def customer_confirm(self):# This function is use for the patient confirmed
        self.ensure_one()
        self.state = 'confirmed'

    # @api.depends('dob')
    # def _compute_age(self):
    #     for record in self:
    #         if record.dob:
    #             today = datetime.datetime.now().date()
    #             age = today.year - record.dob.year - ((today.month, today.day) < (record.dob.month, record.dob.day))
    #             record.age = age


    @api.model
    def create(self, vals):
        record = super().create(vals)
        if record:
            name_text = 'P-010' + str(record.id)
            record.update({'patient_id': name_text,'state': 'created'})
        return record

        # This Function is used for the field Name show with the Customer ID Generate



    def name_get(self):
        res = []
        for record in self:
            patient_name = record.name
            patient_id = record.patient_id or '--'
            res.append((record.id, f"{patient_name} {' '} {patient_id}"))
        return res




    # ------------ This function is used for data retrieve --------------


    def btn_print_excel_report(self):
        filename = self.name
        workbook = xlwt.Workbook(encoding='utf-8')
        sheet1 = workbook.add_sheet('patient', cell_overwrite_ok=True)
        format1 = xlwt.easyxf('align:horiz center;font:color black, bold True;borders: top_color black, bottom_color black, right_color black, left_color black,left thin, right thin, bottom thin,top thin; pattern: pattern solid, fore_color aqua')

        sheet1.col(0).width = 7000
        sheet1.col(1).width = 4000
        sheet1.col(2).width = 7000
        sheet1.col(3).width = 7000
        sheet1.col(4).width = 7000
        sheet1.col(5).width = 5000
        sheet1.col(6).width = 7000
        # sheet1.col(0,0,"Lions Eye & General Hospital",format1)
        # sheet1.col(0,1,format1)
        # sheet1col(0,6,format1)
        # sheet1.col(0,6,format1)
        sheet1.write(0,0,"Name",format1)
        sheet1.write(0,1,"Age",format1)
        sheet1.write(0,2,"Mobile",format1)
        sheet1.write(0,3,"Address",format1)
        sheet1.write(0,4,"Email",format1)
        sheet1.write(0,5,"Gender",format1)
        sheet1.write(0,6,"Created By",format1)

        stream = BytesIO()
        workbook.save(stream)
        out = base64.encodebytes(stream.getvalue())
        excel_id = self.env['custom.excel.class'].create({'datas_name': filename,
                                                         'file_name': out
                                                          })


        return {
            'res_id': excel_id.id,
            'res_model': 'custom.excel.class',
            'name': 'Patient Report',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': False,
            'type': 'ir.actions.act_window'


        }

class CustomExcelPatientReport(models.TransientModel):# Tlhis Class use for thte Excel report
    _name = 'custom.excel.class'
    _rec_name = 'datas_name'


    file_name =fields.Binary(string="Report")
    datas_name = fields.Char(string="File Name")





# -------------------  Note book menu Iten code ----------------

class PatientLineInfo(models.Model):
    _name = 'patient.info.line'

    department = fields.Many2one(string='Department', related='item_name.department')
    price = fields.Float(string='Price', related='item_name.price')
    total_amount = fields.Float(string='Total Amount', related='item_name.total_amount')
    # -------------------------------- Relation change please---------
    item_name = fields.Many2one("item.entry", "Item Name", ondelete='cascade')
    patient_item_id = fields.Many2one('patient.info', "Information")
    quantity = fields.Integer(string="Quantity")


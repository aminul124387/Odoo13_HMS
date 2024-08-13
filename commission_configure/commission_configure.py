from odoo import fields, models, api


# <field name="name" string="Name" filter_domain="['|',('name','ilike',self),('id','ilike',self)]"/>

class Commission_Configure_Info(models.Model):
    _name = 'commission.configure'
    _rec_name = 'commission_id'

    date = fields.Datetime(string="Date of Birth", default=lambda self: fields.Datetime.now())
    commission_id = fields.Char(string='Admission ID', readonly=True)

    doctor_name = fields.Char(string='Doctor Name')
    broker_name = fields.Char(string='Refferel Name')
    mou_start_date=fields.Date(string='MOU Start Date')
    mou_end_date=fields.Date(string='MOU End Date')


    overall_commission_rate = fields.Char(string='Overall All Commission Rate(%)')
    overall_discount_rate = fields.Char(string='Overall All Discount Rate(%)')
    max_discount_rate = fields.Char(string='Max Discount Rate(%)')

    deduct_access_discount_from_com = fields.Boolean(string='Deduct Excess Discount From Commission')
    department_list = fields.Boolean(string='Department List:')
    calculation_base_price=fields.Boolean(string='Calculate on Base Price:')
    total_amount = fields.Char(string='Total Amount')
    # ------------------ Admission Bill Relation
    commission_line_id = fields.One2many('commission.configure.line', 'commission_item_id', required=True)


    state = fields.Selection([('created', 'Created'),
                              ('draft', 'Draft'),
                              ('confirmed', 'Confirmed'),
                              ('cancelled', 'Cancelled')], 'Status', default='draft',
                             readonly=True)

    # --------------------------------Payment Type Rlation --------------------------------------------------------------



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
    @api.model_create_multi
    def print_quotation_report(self):
        return self.env.ref('hospital_Multiple_form.report_ModelName_id').report_action(self)

    # def print_report(self):
    #     data = {
    #         'commission.configure': self.id,
    #     }
    #
    #     return self.env.ref('commission.configure.print_report_pdf').report_action(self, data=data)

    # import pdb
    # pdb.set_trace()
    # This Fuction is used for the Cancel Button ===========================
    def action_cancel(self):
        self.ensure_one()
        self.state = 'cancelled'

    def action_confirm(self):
        self.ensure_one()
        self.state = 'confirmed'

        # This Function is used for Patient ID Generate ==============================

    @api.model
    def create(self, vals):
        record = super().create(vals)
        if record:
            name_text_admission = 'Com-0100' + str(record.id)
            record.update({'commission_id': name_text_admission, 'state': 'created'})
        return record


# --------------------------------------------------  Note book menu Iten code ----------------
# =============================================================================================
class Commission_Configure_Line_Info(models.Model):
    _name = 'commission.configure.line'

    department = fields.Many2one(string='Department', related='item_name.department')
    applicable = fields.Boolean(string='Applicable')
    base_price = fields.Boolean(string='Base Price Applicable')
    fixed_amount = fields.Char(string='Fixed Amount')
    amount = fields.Char(string='Amount(%)')
    test_fees = fields.Char(string='Test Fees')
    commission_amount = fields.Char(string='Commission Amount')
    max_commission_amount = fields.Char(string='Max Commission Amount')


    # -------------------------------- Relation change please---------
    item_name = fields.Many2one("item.entry", "Test Name", ondelete='cascade')
    commission_item_id = fields.Many2one('commission.configure', "Information")






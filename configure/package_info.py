from odoo import fields, models, api
from odoo.exceptions import ValidationError


class packageInfo(models.Model):
    _name = 'package.info'
    _rec_name = 'package_name'

    package_id = fields.Char(string='Package ID', readonly=True)
    package_name = fields.Char(string='package Name')
    package_cate = fields.Selection([
        ('icu', 'ICU'),
        ('nicu', 'NICU'),
        ('emergency', 'Emergency'),
        ('general', 'General'),
        ('eye', 'Eye'),
    ], default='general')
    admission_package = fields.Boolean(string='Admission Package')
    investigation_package = fields.Boolean(string='Investigation Package')
    # admission = fields.One2many('admission.info', 'package_name', 'Admission History', required=False)
    # testname= fields.function(_testname, string="Test Name", type='char')

    state = fields.Selection([('created', 'Created'),
                              ('confirmed', 'Confirmed'),
                              ('notcreated', 'Notcreated'),
                              ('cancelled', 'Cancelled')], 'Status', default='notcreated',
                             readonly=True)
    # ------------------ Admission Line Item Relation --------------------------------------------
    package_line_id = fields.One2many('package.info.line', 'package_item_id', required=True)
    # ----------------------------------------------------------------------------------------------
    discount_percent = fields.Float(string='Discount (%)')
    other_discount = fields.Float(string='Other Discount:', default=0.0, digits='Discount')
    # total_without_discount = fields.Float(string='Total Without Discount', compute='_onchange_total_amount')
    total_without_discount = fields.Float(string='Total Without Discount')
    total = fields.Float(string='Grand Total', compute='', digits='Discount')


    # This Fuction is used for the Cancel Button =========================== item_cancel
    def customer_cancel(self):
        self.ensure_one()
        self.state = 'cancelled'

    def customer_confirm(self):
        self.ensure_one()
        self.state = 'confirmed'

        # This Function is used for package ID Generate

    @api.model
    def create(self, vals):
        record = super().create(vals)
        if record:
            name_text = 'Pk-0100' + str(record.id)
            record.update({'package_id': name_text, 'state': 'created'})
        return record
    #
    #     # This Function is used for the field Name show with the Customer ID Generate

    # @api.model
    # # def name_get(self):
    # #     res = []
    # #     for record in self:
    # #         package_name = record.name
    # #         package_id = record.package_id or '--'
    # #         res.append((record.id, f"{package_name} {' / '} {package_id}"))
    # #     return res

    # ------------ This function is used for data retrieve --------------
    # @api.model
    # def write(self, vals):
    #     change_package = self
    #     if "age" in vals:
    #         newage = vals['age']
    #
    #     return super(packageInfo, self).write(vals)


# --------------------------------------------------  Note book menu Iten code ----------------
#     @api.depends('package_line_id.total_price', 'package_line_id.sub_total_amount', 'other_discount', 'total')
#     def _onchange_total_amount(self):
#         self.total_without_discount = sum(line.total_price for line in self.package_line_id)
#         # This Validation is for Other Discount field Validation
#
#         grand_total = sum(line.sub_total_amount for line in self.package_line_id)
#         self.total = grand_total
#         # self.adv = self.card_amount + self.mfs_amount + self.cash_amount
#         if self.other_discount:
#             self.total = self.total - self.other_discount
#         # self.due_amount = self.total - self.paid


# =============================================================================================
class AdmissionPackageLineInfo(models.Model):
    _name = 'package.info.line'

    department = fields.Many2one(string='Department', related='item_name.department')
    price = fields.Float(string='Price', related='item_name.price')
    # total_price = fields.Float(string='Price', compute='onchange_subtotal_amount')
    total_price = fields.Float(string='Price')
    quantity = fields.Integer("Quantity", default=1)
    # discount = fields.Integer(string='Discount')
    discount_percent = fields.Float(string='Discount (%)', related='package_item_id.discount_percent')
    flat_discount = fields.Float(string='Flat Discount', related='package_item_id.other_discount')
    total_discount = fields.Float(string='Total Discount')
    sub_total_amount = fields.Float(string='Total Amount')
    # -------------------------------- Relation change please---------

    item_name = fields.Many2one("item.entry", "Item Name", ondelete='cascade')
    package_item_id = fields.Many2one('package.info', "Information")

    # @api.depends('price', 'quantity', 'discount_percent')  # This function is used for subtotal product price
    # def onchange_subtotal_amount(self):
    #     for record in self:
    #         record.total_price = record.price * record.quantity
    #         record.total_discount = (record.total_price * record.discount_percent) / 100
    #         record.sub_total_amount = record.total_price - record.total_discount
    #         # Check Quantity Validation for Line Item product -----------
    #         if record.quantity < 0:
    #             raise ValidationError('Your Product Quantity cannot be negative!')



from odoo import fields, models, api


class HospitalItemInfo(models.Model):
    _name = 'item.entry'
    _rec_name='item_name'
    _rec_order = 'item_name desc'

    # name = fields.Many2one('admission.info.line', 'Item Name', ondelete='cascade')


    # admission_line_id = fields.One2many('admission.item', 'addmission_item_id')
    item_name = fields.Char(string='Item Name')
    department = fields.Many2one('department.config', string='Department')
    price = fields.Float(string='Price')

    has_auto_select_admission = fields.Boolean(string='Item Auto Select Field(Admission)')
    has_service_charge = fields.Boolean(string='Service Charge')
    more_than_one_days = fields.Boolean(string='If Hour Base Calculate')
    discount = fields.Float(string='Discount')
    discount_percent = fields.Float(string='Discount (%)')
    flat_discount = fields.Float(string='Flat Discount')
    total_discount = fields.Float(string='Total Discount')
    total_amount = fields.Float(string='Total Amount')
    account_id = fields.Char(string='Account ID')
    sample_type = fields.Selection([('blood', 'Blood'),
                              ('stool', 'Stool'),
                              ('urine', 'Urine'),
                              ('other', 'Other')], default='blood')
    state = fields.Selection([('created', 'Created'),
                              ('confirmed', 'Confirmed'),
                              ('notcreated', 'Notcreated'),
                              ('cancelled', 'Cancelled')], 'Status', default='notcreated',
                             readonly=True)

    base_rate = fields.Integer(string='Base Rate')
    sample_required_date = fields.Integer(string='Sample Required Time')
    sample_required = fields.Boolean(string='Sample Required')
    individual = fields.Boolean(string='Individual')
    manual = fields.Boolean(string='Manual')
    merge = fields.Boolean(string='Merge')
    dependency = fields.Boolean(string='Dependency')
    no_lab_required = fields.Boolean(string='No Lab Required')
    indoor_item = fields.Boolean(string='Indoor Item')
    sample_type = fields.Selection([('blood', 'Blood'),
                                    ('none', 'None'),
                                    ('stool', 'Stool'),
                                    ('urine', 'Urine'),
                                    ('other', 'Other')], default='none')


    item_entry_line_id = fields.One2many('item.entry.line', 'item_entry_ids')
    item_entry_merge_line_id = fields.One2many('item.merge.line', 'item_merge_item_ids')

#---------------------------------------------------------------------------------------------

    #-- This Function are used for the action of button ------------------
    def item_cancel(self):
        self.ensure_one()
        self.state = 'cancelled'

    def item_confirmed(self):
        self.ensure_one()
        self.state = 'confirmed'
#-----------------------------------------------------------------------------------------------

class HospitalLineItemInfo(models.Model):
    _name = 'item.entry.line'



    name = fields.Char(string='Item')
    reference_value = fields.Char(string='Reference Value')
    bold = fields.Boolean(string='Bold')
    group_by = fields.Boolean(string='Group By')
    others = fields.Char(string='Others')
    item_entry_ids = fields.Many2one('item.entry', "Item Info")

class HospitalItemMergeLineInfo(models.Model):
    _name = 'item.merge.line'



    name = fields.Char(string='Unknown Item')
    item_merge_item_ids = fields.Many2one('item.entry', "Item Info")
from gevent.subprocess import value

from odoo import fields, models, api
from odoo.exceptions import UserError
from _datetime import datetime
from odoo.tools import html_escape

from odoo.exceptions import ValidationError


class InventoryInfo(models.Model):
    _name = 'inventory.info'
    _rec_name = 'ipe'

    date = fields.Datetime(string="Date", default=lambda self: fields.Datetime.now())
    ipe = fields.Char(string='Entry No.', readonly=True)
    ref = fields.Char(string='Reference')
    invoice_no = fields.Char(string='Invoice No.')
    partner_id = fields.Many2one('res.users', string='Employee Name')
    warehouse = fields.Many2one('stock.location', string='Warehouse')
    department = fields.Many2one('department.config', string='Department')
    total = fields.Float("Total Amount")
    state = fields.Selection([('draft', 'Draft'),
                              ('validate', 'Validate'),
                              ('confirmed', 'Confirmed'),
                              ('cancelled', 'Cancelled')], 'Status', default='draft',
                             readonly=True)

    inventory_line_id = fields.One2many('inventory.info.line', 'inventory_item_name', 'inventory Info')

    @api.model
    def create(self, vals):
        record = super().create(vals)
        if record:
            name_text_ipe = 'IPE-1000' + str(record.id)
            record.update({'ipe': name_text_ipe, 'state': 'draft'})

        return record

        # =====================================================================
        # calculating total
    @api.onchange('inventory_line_id') # IPE all Product Total Calculate
    def onchange_product_line_total(self):
        sumallproduct = 0
        for item in self.inventory_line_id:
            sumallproduct = sumallproduct + item.total_price

        self.total = sumallproduct


    # def inventory_confirm(self):
    #     if self.state == 'confirmed':
    #         raise ValidationError("Inventory is already confirmed.")
    #     elif self.state == 'cancelled':
    #         raise ValidationError('This Inventory is Cancelled and cannot be Confirmed.')
    #
    #     self.state = 'confirmed'
    #
    #     if self.total > 0:
    #         jr_payment = self.env['journal.receipt'].create({
    #             'date': self.date,
    #             'ipe': self.id,
    #             'total': self.total,
    #             'ref': self.ref
    #         })


    def inventory_product_receive(self):
        cc_ids = self.ids
        for id in cc_ids:
            ir_obj = self.browse(id)
            if ir_obj.state == 'confirmed':
                raise UserError("Sorry, it is already confirmed.")

            stock_picking_type = self.env['stock.picking.type'].search([
                ('warehouse_id', '=', ir_obj.warehouse_id.id), ('code', '=', 'incoming')
            ], limit=1)

            sorce_id = stock_picking_type.default_location_src_id.id
            dest_id = stock_picking_type.default_location_dest_id.id
            picking_type_id = stock_picking_type.id

            grn_vals = {
                'partner_id': ir_obj.partner_id.id,
                'date': fields.Datetime.now(),
                'origin': ir_obj.name,
                'move_type': 'one',
                'invoice_state': 'none',
                'picking_type_id': picking_type_id,
            }

            move_lines = []
            line_ids = []

            for items in ir_obj.inventory_product_entry_line_ids:
                move_lines.append((0, 0, {
                    'product_id': items.product_name.id,
                    'product_uom': 1,
                    'product_uom_qty': items.quantity,
                    'product_uos_qty': items.quantity,
                    'price_unit': items.unit_price,
                    'name': ir_obj.name,
                    'location_id': sorce_id,
                    'location_dest_id': dest_id,
                    'invoice_state': 'none',
                }))

                line_ids.append((0, 0, {
                    'name': ir_obj.name,
                    'partner_id': ir_obj.partner_id.id,
                    'account_id': items.account_id.id,
                    'debit': items.total_price,
                    'credit': 0,
                }))

            grn_vals['move_lines'] = move_lines

            grn = self.env['stock.picking'].create(grn_vals)

            stock_picking = self.env['stock.picking'].browse(grn.id)
            stock_picking.action_confirm()

            stock_picking.do_enter_transfer_details()
            trans_search = self.env['stock.transfer_details'].search([('picking_id', '=', stock_picking.id)], limit=1)
            trans_browse = self.env['stock.transfer_details'].browse(trans_search)
            trans_browse.do_detailed_transfer()

            # Journal Creation
            period_id = self.env['account.period'].search([], limit=1)
            cc_obj = self.browse(id)

            line_ids.append((0, 0, {
                'name': cc_obj.name,
                'partner_id': cc_obj.partner_id.id,
                'account_id': cc_obj.partner_id.property_account_payable.id,
                'debit': 0,
                'credit': cc_obj.total,
            }))

            j_vals = {
                'name': '/',
                'journal_id': 6,  # Advance Cash Journal
                'date': fields.Date.today(),
                'period_id': period_id.id,
                'ref': cc_obj.name,
                'line_ids': line_ids,
            }

            jv_entry = self.env['account.move'].create(j_vals)
            jv_entry.action_post()

            # Update inventory_product_entry state, grn_id, and grn_journal_id
            self.env.cr.execute("""
                UPDATE inventory_product_entry
                SET state = 'confirmed',
                    grn_id = %s,
                    grn_journal_id = %s
                WHERE id = %s
            """, (grn.id, jv_entry.id, id))

            self.env.cr.commit()

        return True



    #
    # # This function used opd ticket Cancelled with Money receipt Cancelled
    def inventory_cancel(self):
        self.ensure_one()
        if self.state == 'cancelled':
            raise UserError('Inventory is already cancelled.')
        self.state = 'cancelled'
        money_receipts = self.env['money.receipt'].search([('ipe', '=', self.id)])
        money_receipts.write({'state': 'cancelled'})
        return True




class InventoryLineInfo(models.Model):
    _name = 'inventory.info.line'

    product_name = fields.Many2one('product.template', string='Product Name')
    account = fields.Char(string='Account No.')
    quantity = fields.Integer(string='Quantity', default=1)
    unit_price = fields.Float(string='Unit Price')
    total_price = fields.Float(string='Total', compute='onchange_subtotal_amount')
    # -------------------------------- Relation change please ---------
    inventory_item_name = fields.Many2one('inventory.info', "Information", required=True)

    @api.depends('unit_price', 'quantity', 'total_price')
    def onchange_subtotal_amount(self):
        for record in self:
            record.total_price = record.unit_price * record.quantity

# -*- coding: utf-8 -*-

from odoo import models, api, _


class ResCompany(models.Model):
    _inherit = 'res.company'

    # ------------------------------------------------------------------
    # stock return sequence
    # ------------------------------------------------------------------
    def _create_return_sequence(self):
        vals = []
        for company in self:
            vals.append({
                'name': ' '.join([_('Return'), company.name]),
                'code': 'stock.return',
                'company_id': company.id,
                'prefix': 'RET/',
                'padding': 5,
            })
        if vals:
            lang = self.env.user.lang
            self.env['ir.sequence'].sudo().with_context(lang=lang).create(vals)

    @api.model
    def create_missing_return_sequence(self):
        company_ids = self.env['res.company'].search([])
        company_has_return_seq = self.env['ir.sequence'].search(
            [('code', '=', 'stock.return')]).mapped('company_id')
        company_todo_sequence = company_ids - company_has_return_seq
        company_todo_sequence._create_return_sequence()

    # ------------------------------------------------------------------
    # stock return picking type
    # ------------------------------------------------------------------
    def _create_return_picking_type(self):
        vals = []
        PickingType = self.env['stock.picking.type']
        for company in self:
            sequence = self.env['ir.sequence'].search([
                ('code', '=', 'stock.return'),
                ('company_id', '=', company.id),
            ])
            warehouse = self.env['stock.warehouse'].search([
                ('company_id', '=', company.id),
            ], limit=1)
            # choose the next available color for the operation types of this warehouse
            all_used_colors = [res['color'] for res in PickingType.search_read([('warehouse_id', '!=', False), ('color', '!=', False)], ['color'], order='color')]
            available_colors = [zef for zef in range(0, 12) if zef not in all_used_colors]
            color = available_colors[0] - 1 if available_colors else 0
            # suit for each sequence
            max_sequence = self.env['stock.picking.type'].search_read([('sequence', '!=', False)], ['sequence'], limit=1, order='sequence desc')
            max_sequence = max_sequence and max_sequence[0]['sequence'] or 0
            vals.append({
                'name': _('Return'),
                'code': 'outgoing',
                'use_create_lots': False,
                'use_existing_lots': True,
                'sequence': max_sequence + 1,
                'sequence_id': sequence.id,
                'color': color,
                'default_location_src_id': warehouse.lot_stock_id.id,
                'default_location_dest_id': self.env.ref('stock.stock_location_suppliers').id,
                'barcode': warehouse.code.replace(" ", "").upper() + "-RETURN",
                'sequence_code': 'RET',
                'warehouse_id': warehouse.id,
                'company_id': company.id,
            })
        if vals:
            lang = self.env.user.lang
            self.env['stock.picking.type'].sudo().with_context(lang=lang).create(vals)

    @api.model
    def create_missing_return_picking_type(self):
        company_ids = self.env['res.company'].search([])
        company_has_return_picking_type = (
            self.env['stock.picking.type'].sudo().search([
                ('default_location_dest_id.usage', '=', 'supplier'),
            ]).mapped('company_id')
        )
        company_todo_picking_type = company_ids - company_has_return_picking_type
        company_todo_picking_type._create_return_picking_type()

    # ------------------------------------------------------------------
    # stock return rule
    # ------------------------------------------------------------------
    def _create_return_rule(self):
        vendor_location = self.env.ref('stock.stock_location_suppliers')

        vals = []
        lang = self.env.user.lang
        route_obj = self.env['stock.location.route']
        for company in self:
            return_route = route_obj.sudo().with_context(lang=lang).create({
                'name': _("Return"),
                'sequence': 3,
                'company_id': company.id,
            })
            return_picking = self.env['stock.picking.type'].sudo().search([
                ('company_id', '=', company.id),
                ('default_location_dest_id', '=', vendor_location.id),
            ], limit=1, order='sequence')
            src_location = return_picking.default_location_src_id
            vals.append({
                'name': '%s → %s' % (
                    src_location.name, vendor_location.name),
                'action': 'pull',
                'location_src_id': src_location.id,
                'location_id': vendor_location.id,
                'procure_method': 'make_to_stock',
                'route_id': return_route.id,
                'picking_type_id': return_picking.id,
                'company_id': company.id,
                'warehouse_id': return_picking.warehouse_id.id,
            })
        if vals:
            self.env['stock.rule'].sudo().with_context(lang=lang).create(vals)

    @api.model
    def create_missing_return_rule(self):
        return_picking_types = self.env['stock.picking.type'].search([
            ('default_location_dest_id.usage', '=', 'supplier'),
        ])

        company_ids = self.env['res.company'].search([])
        company_has_return_rule = self.env['stock.rule'].search(
            [('picking_type_id', 'in', return_picking_types.ids)]).mapped('company_id')
        company_todo_rule = company_ids - company_has_return_rule
        company_todo_rule._create_return_rule()

# -*- coding: utf-8 -*-

from odoo import models, api


class Warehouse(models.Model):
    _inherit = 'stock.warehouse'

    @api.model
    def create(self, vals):
        warehouse = super(Warehouse, self).create(vals)
        company = warehouse.company_id
        company._create_return_sequence()
        company._create_return_picking_type()
        company._create_return_rule()
        return warehouse

# -*- coding: utf-8 -*-
from . import models

from odoo import api, SUPERUSER_ID

lang_todo = ['ar_001', 'id_ID', 'en_US']

def _auto_install_l10n(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    mods = env['ir.module.module'].search(
        [('state', '=', 'installed')]).mapped('name')
    mods.append('stock_return')
    mods = list(set(mods))
    env['ir.translation']._load_module_terms(mods, lang_todo)

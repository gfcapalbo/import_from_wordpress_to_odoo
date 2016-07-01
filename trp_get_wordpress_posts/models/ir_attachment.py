# -*- coding: utf-8 -*-
from openerp import models, fields


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'
    origin_wp_site = fields.Many2one(
            string='wp.wordpress site', 
            comodel_name='wp.wordpress.site')
    imported_wp = fields.Boolean('Imported from wordpress')


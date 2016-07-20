# -*- coding: utf-8 -*-
from openerp import models, fields


class BlogCategory(models.Model):
    _inherit = 'blog.category'

    origin_wp_site = fields.Many2one(
            string='wp.wordpress site', 
            comodel_name='wp.wordpress.site')
    imported_wp = fields.Boolean('Imported from wordpress')


# -*- coding: utf-8 -*-
from openerp import models, fields


class blog_post(models.Model):
    
    _inherit = 'blog.post'

    origin_wp_site = fields.Many2one(
            string='wp.wordpress site', 
            comodel_name='wp.wordpress.site')
    imported_wp = fields.Boolean('Imported from wordpress')



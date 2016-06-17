# -*- coding: utf-8 -*-
from openerp import models, fields


class wp_pagedump(models.Model):
    _name = 'wp.pagedump'

    origin_wp_site = fields.Many2one(
            string='wp.wordpress site', 
            comodel_name='wp.wordpress.site')
    imported_wp = fields.Boolean('Imported from wordpress')
    HtmlDump = fields.Html('Page_dump')
    Title = fields.Char('Title')

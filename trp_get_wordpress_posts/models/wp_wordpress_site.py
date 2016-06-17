# -*- coding: utf-8 -*-
from openerp import models, fields, api


class WordpressSite(models.Model):
    _name = 'wp.wordpress.site'
    _rec_name = 'WP_LOC'

    WP_USR = fields.Char('Wordpress User', required=True)
    WP_PWD = fields.Char('Wordpress password', required=True)
    WP_LOC = fields.Char('wordpress location', required=True)

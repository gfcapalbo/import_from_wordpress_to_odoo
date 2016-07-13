# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import fields, models


class wp_user(models.Model):
    _name = 'wp.user'

    associated_odoo_partner = fields.Many2one(
        comodel_name='res.users', 
        string="Associated odoo user"
    )
    wp_id = fields.Integer(string="Wordpress id", readonly=True)
    wp_nicename = fields.Char(string="Wordpress Nicename", readonly=True)
    wp_nickname = fields.Char(string="Wordpress Nickname", readonly=True)
    wp_display_name = fields.Char(string="Wordpress Display Name", readonly=True)
    wp_first_name = fields.Char(string="Wordpress First Name", readonly=True)
    wp_last_name = fields.Char(string="Wordpress Last Name", readonly=True)
    wp_email = fields.Char(string="Wordpress email", readonly=True)
    origin_wp_site = fields.Many2one(
        string='wp.wordpress site',
        comodel_name='wp.wordpress.site'
    )


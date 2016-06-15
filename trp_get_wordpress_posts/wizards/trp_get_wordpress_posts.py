# -*- coding: utf-8 -*-
import sys, os
from openerp import api, fields, models
from wordpress_xmlrpc import Client as WPClient
from wordpress_xmlrpc.methods import posts as method_posts
from wordpress_xmlrpc.methods import taxonomies as method_taxonomies 
from wordpress_xmlrpc.methods import users as method_users 
from wordpress_xmlrpc.methods import media as method_media
import wget
import requests
from openerp.tools import image_save_for_web


class WpImportBlogPosts(models.TransientModel):

    _name = "wp.import.blog.post"
    _description = 'import blogposts from wordpress'

    WP_USR = fields.Char('Wordpress User')
    WP_PWD = fields.Char('Wordpress password')
    WP_LOC = fields.Char('wordpress location')
    ODOO_USR = fields.Char('Odoo User')
    ODOO_PWD = fields.Char('Odoo Pwd')

    @api.multi
    def get_all_images(self):
        try:
            wpclient = WPClient(self.WP_LOC, self.WP_USR, self.WP_PWD)
        except:
            sys.exit('connection failed')
        medialibrary = wpclient.call(method_media.GetMediaLibrary(
            {'parent_id': ''}))
        for media in medialibrary:
            if 'file'in media.metadata:
                filename = media.metadata['file']
                onlyname = os.path.basename(filename)
                fetched_file = requests.get(media.link)
                attachment_model = self.env['ir.attachment']
                attachment_dict = {
                    'name': onlyname,
                    'datas': fetched_file.content.encode('base64'),
                    'datas_fname': onlyname,
                    'res_model': 'ir.ui.view',
                }
            attachment_model.create(attachment_dict)

    @api.multi
    def import_posts(self):
        try:
            wpclient = WPClient(self.WP_LOC, self.WP_USR, self.WP_PWD)
        except:
            sys.exit('connection failed')
        posts = wpclient.call(method_posts.GetPosts())
        taxonomies = wpclient.call(method_taxonomies.GetTaxonomies())
        for taxonomy in taxonomies:
            if taxonomy.name == 'post_tag':
                blogposts = taxonomy.name
        terms = wpclient.call(method_taxonomies.GetTerms(blogposts))
        #create tags
        tagmapping = {}
        for term in terms:
            tagsearch = [('name', '=', term.name)]
            existing_tags = self.env['blog.tag'].search(tagsearch)
            tagdict = {'name': term.name}
            #If a tag with that name exists please skip creation
            if not existing_tags:
                newid = self.env['blog.tag'].create(tagdict)
            else:
                newid = existing_tags[0]
            tagmapping[term.id] = newid.id
        for post in posts:
            tag_ids = []
            for wp_tag_id in post.struct['terms']['post_tag']:
                tag_ids.append(tagmapping[str(wp_tag_id)])
            bpdict = {
                    'tag_ids': [[6, False, tag_ids]],
                    'blog_id': 1,
                    'content': post.content,
                    'write_date': post.date,
                    'website_published': (post.post_status == 'publish'),
                    'name': post.title or 'no_name',
                }
            new_bp = self.env['blog.post'].create(bpdict)
            #Get media library for this blogpost
            medialibrary = wpclient.call(method_media.GetMediaLibrary(
                {'parent_id': post.id})
            )
            for media in medialibrary:
                #import image
                #get only files
                if 'file'in media.metadata:
                    filename = media.metadata['file']
                    onlyname = os.path.basename(filename)
                    fetched_file = requests.get(media.link)
                    attachment_model = self.env['ir.attachment']
                    attachment_dict = {
                        'name': onlyname,
                        'datas': fetched_file.content.encode('base64'),
                        'datas_fname': onlyname,
                        'res_model': 'ir.ui.view',
                    }
                    att = attachment_model.create(attachment_dict)
                    replaced = new_bp.content.replace(
                        "http://therp.nl/wp-content/uploads/" + 
                        str(media.metadata['file']),
                        "/website/image/ir.attachment/"+str(att.id)+
                        "/datas/"+str(media.metadata['height'])+
                        "x"+str(media.metadata['width'])
                    )
                    new_bp.write({'content': replaced})            

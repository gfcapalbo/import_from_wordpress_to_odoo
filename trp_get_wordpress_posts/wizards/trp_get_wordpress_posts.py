# -*- coding: utf-8 -*-
import sys
import os
from openerp import api, fields, models
from wordpress_xmlrpc import Client as WPClient
from wordpress_xmlrpc.methods import posts as method_posts
from wordpress_xmlrpc.methods import pages as method_pages
from wordpress_xmlrpc.methods import taxonomies as method_taxonomies
from wordpress_xmlrpc.methods import media as method_media
import requests


class WpImportBlogPosts(models.TransientModel):

    _name = "wp.import.blog.post"
    _description = 'import blogposts from wordpress'

    websitename_hardcoded = 'https://therp.nl/'

    WP_SITE = fields.Many2one(
        string='From site', comodel_name='wp.wordpress.site'
    )
    delete_old = fields.Boolean(
        string='Delete all previously imported data'
               'from this wordpress website'
    )

    def replacelast(self, s, old, new, how_many_from_last):
        li = s.rsplit(old, how_many_from_last)
        return new.join(li)

    def create_odoo_attachment(self, media):
            if 'file'in media.metadata:
                filename = media.metadata['file']
                onlyname = os.path.basename(filename)
                fetched_file = requests.get(
                    media.link.replace('http', 'https', 1)
                )
                attachment_dict = {
                    'name': onlyname,
                    'datas': fetched_file.content.encode('base64'),
                    'datas_fname': onlyname,
                    'type': 'binary',
                    'res_model': 'ir.ui.view',
                    'imported_wp': True,
                    'origin_wp_site': self.WP_SITE.id,
                }
            return self.env['ir.attachment'].sudo().create(attachment_dict)

    def create_odoo_thumbnail(self, media):
            if media['metadata']['file']:
                filename = media['metadata']['file']
                onlyname = os.path.basename(filename)
                fetched_file = requests.get(
                    media['link'].replace('http', 'https', 1)
                )
                attachment_dict = {
                    'name': onlyname,
                    'datas': fetched_file.content.encode('base64'),
                    'datas_fname': onlyname,
                    'type': 'binary',
                    'res_model': 'ir.ui.view',
                    # todo make it blog.post in case of thumbs
                    'imported_wp': True,
                    'origin_wp_site': self.WP_SITE.id,
                }
            return self.env['ir.attachment'].sudo().create(attachment_dict)

    @api.multi
    def get_all_images(self):
        try:
            wpclient = WPClient(
                self.WP_SITE.WP_LOC, self.WP_SITE.WP_USR, self.WP_SITE.WP_PWD)
        except:
            sys.exit('connection failed')
        medialibrary = wpclient.call(method_media.GetMediaLibrary(
            {'parent_id': ''}))
        for media in medialibrary:
            self.create_odoo_attachment(media)

    @api.multi
    def import_posts(self):
        try:
            wpclient = WPClient(
                self.WP_SITE.WP_LOC, self.WP_SITE.WP_USR, self.WP_SITE.WP_PWD)
        except:
            sys.exit('connection failed')
        # DELETE old tags, posts, and attacments.
        if self.delete_old:
            self.env['blog.post'].search([
                ('imported_wp', '=', True),
                ('origin_wp_site', '=', self.WP_SITE.id)
                ]).sudo().unlink()
            self.env['blog.tag'].search([
                ('imported_wp', '=', True),
                ('origin_wp_site', '=', self.WP_SITE.id)
                ]).sudo().unlink()
            self.env['ir.attachment'].search([
                ('imported_wp', '=', True),
                ('origin_wp_site', '=', self.WP_SITE.id)
                ]).sudo().unlink()
            self.env['wp.pagedump'].search([
                ('imported_wp', '=', True),
                ('origin_wp_site', '=', self.WP_SITE.id)
                ]).sudo().unlink()

        pages = wpclient.call(method_pages.GetPageTemplates())
        for key, value in pages.iteritems():
            page_path = self.websitename_hardcoded + value
            fetch_page = requests.get(page_path)
            page_dict = {
                    'Title': key,
                    'HtmlDump': fetch_page.content,
                    'imported_wp': True,
                    'origin_wp_site': self.WP_SITE.id,
                    }
            self.env['wp.pagedump'].sudo().create(page_dict)
        taxonomies = wpclient.call(method_taxonomies.GetTaxonomies())
        for taxonomy in taxonomies:
            if taxonomy.name == 'post_tag':
                blogposts = taxonomy.name
        terms = wpclient.call(method_taxonomies.GetTerms(blogposts))
        # create tags
        tagmapping = {}
        for term in terms:
            tagsearch = [('name', '=', term.name)]
            existing_tags = self.env['blog.tag'].search(tagsearch)
            tagdict = {
                    'name': term.name,
                    'origin_wp_site': self.WP_SITE.id,
                    'imported_wp': True,
                    }
            # If a tag with that name exists please skip creation
            if not existing_tags:
                newid = self.env['blog.tag'].sudo().create(tagdict)
            else:
                newid = existing_tags[0]
            tagmapping[term.id] = newid.id
        """
        forced to use this when counting blog posts
        there is a broken/malformed post in our wordpress that 
        returns an error and blocks the whole import
        We are forced to get them one by one in a try/except
        so we can skip the failures, that means slower performance
        but more stable import
        """
        offset = 0
        number = 1
        post_num = 0
        wp_bp_id_list = []
        while True:
            postcount = wpclient.call(method_posts.GetPosts(
                {'number': number, 'offset': offset}))
            if len(postcount) == 0:
                break
            offset += 1
            post_num += number
            wp_bp_id_list.append(int(postcount[0].id))
        posts = []
        for pst_id in wp_bp_id_list:
            try:
                posts.append(
                    wpclient.call(method_posts.GetPost(pst_id))
                )
            except:
                continue
        for post in posts:
            tag_ids = []
            if 'post_tag' in post.struct['terms']:
                for wp_tag_id in post.struct['terms']['post_tag']:
                    tag_ids.append(tagmapping[str(wp_tag_id)])
            bpdict = {
                    'tag_ids': [[6, False, tag_ids]],
                    'blog_id': 1,
                    'content': post.content,
                    'write_date': post.date,
                    'website_published': (post.post_status == 'publish'),
                    'name': post.title or 'no_name',
                    'origin_wp_site': self.WP_SITE.id,
                    'imported_wp': True,
                    # info for the website_blog_teaser module
                    'display_type': 'teaser',
                    'extract_auto': True,
                    'subtitle': ' ',
                    # info for website_blog_no_background_image
                    'background_image_show': 'no_image'
                }
            blog_thumbnail = post.struct['post_thumbnail']
            if blog_thumbnail:
                try:
                    blogpost_thumbnail = self.create_odoo_thumbnail(
                        blog_thumbnail
                    )
                    bpdict['thumbnail'] = blogpost_thumbnail.id,
                except:
                    pass
            new_bp = self.env['blog.post'].sudo().create(bpdict)
            # Get media library for this blogpost
            medialibrary = wpclient.call(method_media.GetMediaLibrary(
                {'parent_id': post.id})
            )
            replaced = new_bp.content
            for media in medialibrary:
                if 'file'in media.metadata:
                    att = self.create_odoo_attachment(
                        media)
                    path_and_file = media.metadata['file']
                    onlyname = os.path.basename(path_and_file)
                    onlypath = self.replacelast(path_and_file, onlyname, '', 1)
                    # try replacing main file in content
                    source = "http://therp.nl/wp-content/uploads/" + \
                        path_and_file
                    height = str(media.metadata['height'])
                    width = str(media.metadata['width'])
                    replaced = replaced.replace(
                        source,
                        "/website/image/ir.attachment/" + str(att.id) +
                        "/datas/" + height +
                        "x" + width)
                    """
                    we do not know wich size will be passed so try them all
                    by iterating all size keys, including thumbnails
                    """
                    if 'sizes' in media.metadata:
                        for size in media.metadata['sizes']:
                            if size != 'thumbnail':
                                source = (
                                    "http://therp.nl/wp-content/"
                                    "uploads/%s%s"
                                    ) % (
                                        onlypath,
                                        str(media.metadata['sizes'][size]['file'])
                                        )
                                height = str(
                                    media.metadata['sizes'][size]['height']
                                )
                                width = str(
                                    media.metadata['sizes'][size]['width']
                                )
                                replaced = replaced.replace(
                                    source,
                                    "/website/image/ir.attachment/" + 
                                    str(att.id) +
                                    "/datas/" + height +
                                    "x" + width)
                    new_bp.write({'content': replaced})
            # update date with wordpress
            SQL = "UPDATE blog_post set create_date = '%s' where id = %s" % (
                post.date, new_bp.id)
            self.env.cr.execute(SQL)

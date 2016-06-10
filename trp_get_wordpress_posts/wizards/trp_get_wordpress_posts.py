# -*- coding: utf-8 -*-
import sys
from openerp import models, fields
from wordpress_xmlrpc import Client as WPClient
from wordpress_xmlrpc.methods import posts as method_posts
from wordpress_xmlrpc.methods import taxonomies as method_taxonomies 
from wordpress_xmlrpc.methods import users as method_users 


class WpImportBlogPosts(models.TransientModel):

    _name="wp.Import.blog.post"
    _description = 'import blogposts from wordpress'

    WP_USR=fields.Char('Wordpress User')
    WP_PWD=fields.Char('Wordpress password')
    WP_LOC=fields.Char('wordpress location')
    ODOO_USR=fields.Char('Odoo User')
    ODOO_PWD=fields.Char('Odoo Pwd')


    def import_posts(self):
        #'https://therp.nl/xmlrpc.php',
        try:
            wpclient = WPClient(WP_LOC, WP_USR, WP_PWD)
        except:
            sys.exit('connection failed')

        posts = wpclient.call(method_posts.GetPosts())
        users = wpclient.call(method_users.GetUsers())
        taxonomies = wpclient.call(method_taxonomies.GetTaxonomies())
        for taxonomy in taxonomies:
            if taxonomy.name == 'post_tag':
                blogposts=taxonomy.name
        terms = wpclient.call(method_taxonomies.GetTerms(blogposts))

        #create tags
        tagmapping={}
        for term in terms:
            tagsearch=[('name', '=', term.name)]
            existing_tags=sock.execute_kw(
                    ODOO_DB,uid,ODOO_PWD,'blog.tag', 'search', [tagsearch])
            tagdict = {'name': term.name}
            #If a tag with that name exists please skip creation
            if not existing_tags:
                newid = sock.execute_kw(
                    ODOO_DB,uid,ODOO_PWD, 'blog.tag', 'create', [tagdict])
            else:
                newid = existing_tags[0]
            tagmapping[term.id] = newid
        for post in posts:
            tag_ids=[]
            for wp_tag_id in  post.struct['terms']['post_tag']:
                tag_ids.append(tagmapping[str(wp_tag_id)])
            bpdict = {}
            bpdict['tag_ids'] = [[6, False, tag_ids]]
            bpdict['blog_id'] = 1
            bpdict['content'] = post.content
            bpdict['write_date'] = post.date    
            bpdict['create_uid'] = 1
            bpdict['website_published'] = (post.post_status == 'publish')
            bpdict['write_uid'] = 3    #imposing Anne's ID as creator
            bpdict['name'] = post.title
            bpdict['background_image_show'] = 'no_image'
            self.Env['blog.post'].create(bpdict)




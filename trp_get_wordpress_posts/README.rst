.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3
=======================
trp_get_wordpress_posts
=======================

This module allows to import all information from one or many wordpress websites 
into odoo.  (Blogposts with images and tags, Image assets, PHP page dumps)


Installation
============

DEPENDENCIES:

This module depends on requests libtary (already installed if you have odoo installed)
and  python-wordpress-xmlrpc.

    to install:

    pip install python-wordpress-xmlrpc

    (tested with version 2.3)


Configuration
=============

In the menu "Knowledge>Import from wordpress" Choose Wordpress Websites to create the 
connections to the websites you want to import.

Every website must have:

        Location: Location of your wordpress XMLRPC interface
                  Usually <MY COMPLETE WEBSITE ADDRESS>/xmlrpc.php
        Username: Wordpress Username
        
        Password: Wordpress Password


XMLRPC ACCESS:
From wordpress 4.1 XMLRPC is enabled by default. If you have problems connecting please verify your address, 
and also youe webserver settings, to be sure the page has not been blocked.


Usage
=====

To use this module, you need to:

click on  "Import Wordpress Blog" to launch a wizard that will ask you to specify the website to import from and 
if should delete all previously imported assets.

It will import All blogposts with images (created as odoo website attachemtns) and 
available in attachments dir) and tags. It will also create a dump of all wordpress
page templates availiable in "wordpress pagedumps".


IMPORTANT NOTES ON IMPORT:
THe import will fetch only the records the specified user has the right to access in wordpress,
so for a complete import , please specify a user with complete access to all data.

All records will be created as odoo "Administrator".

The "delete previously imported" will delete all older  assets fron that website (it will not delete assets from other
websites.  If not selected the import will add duplicate records.




* go to ...
.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
    :alt: Try me on Runbot
    :target: https://runbot.odoo-community.org/runbot/{repo_id}/8.0

.. repo_id is available in https://github.com/OCA/maintainer-tools/blob/master/tools/repos_with_ids.txt

For further information, please visit:

* https://www.odoo.com/forum/help-1

Known issues / Roadmap
======================

Next features:

0. Import Stats after import (added / deleted) and some feedback while importing

1.Mapping of odoo users to wordpress users.

2.Blog Thumbnail image.

3.Show origin website in blogposts.

4.Creation of one new blog per website instead of adding to default odoo blog.



Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/import_from_wordpress_to_odoo/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback
`here <https://github.com/OCA/import_from_wordpress_to_odoo/issues/new?body=module:%20trp_get_wordpress_posts%0Aversion:%208.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Credits
=======

Contributors
------------

* Giovanni Francesco Capalbo  <giovanni@therp.nl>

Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.

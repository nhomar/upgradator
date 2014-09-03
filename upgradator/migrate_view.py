#!/bin/python
from xml.etree import ElementTree
from lxml import etree


class migrate_view():

    '''
    Migrate architecture view to use it in the verision 7 
    '''

    def __init__(self, l_file=None):
        '''
        Maiker to init path with the xml files
        @param l_file List with xml file path
        '''

        self.files = l_file and type(l_file) is list and l_file or l_file \
            and [l_file]

    def change_xpath(self, xml_f):
        '''
        Change the path from xpath using the relative rute 
        @param xml_f Type Object xpath from lxml.tree library
        '''
        xpath_list = xml_f.xpath('//xpath')
        if xpath_list:
            for xpaths in xpath_list:
                expr = xpaths.attrib.get('expr', False)
                if expr:
                    m = '//' in expr and expr or  expr.split('/') and \
                        '//%s' % expr.split('/')[-1]
                    xpaths.set('expr', m)

        return True

    def remove_depreciated(self, xml_o):
        '''
        Remove depreceated methos in the architecture view
        @param xml_o Type Object xpath from lxml.tree library

        '''
        types = xml_o.xpath('//field[@name="type"]')
        if types:
            for line in types:
                parent = line.getparent()
                parent.remove(line)
        types = xml_o.xpath('//field[@mode]')
        if types:
            for line in types:
                line.attrib.get('mode', False) and \
                    line.attrib.pop('mode')

        return True

    def version_7(self, xml_o):
        '''
        Add Version 7 in tags form 
        @param xml_o Type Object xpath from lxml.tree library

        '''
        x = xml_o.xpath('//form')
        if x:
            for i in x:
                i.set('version', '7.0')

        return True

    def get_attr(self, xml_f, xpaths, attrb):
        '''
        Send the attribute in the specification tag 
        @param xml_f Type Object xpath from lxml.tree library
        @param xpaths Point of search 
        @param attrb Attribute to return 
        '''
        xpath_list = xml_f.xpath('//%s' % xpaths)
        expr = []
        if xpath_list:
            for xpaths in xpath_list:
                for i in xpaths.getchildren():

                    expr.append((i.tag, i.attrib.items()))

        return expr

    def search_model(self, l_files, t_search='model', mo_list=None):
        '''
        Search model in view to show if module or module  was 
        changed or deleted
        @param l_files List with file path xml
        @param t_search Type search, in this field you can search if the views
        are inherit with some module or model
                        'model' Only search model in the view
                        'module' Only search modules in the view
                        'all' Search model and modules that are inside mo_list 
        '''

        l_files = self.files or l_files and type(l_files) is list or \
            l_files and [l_files]

        for files in mo_list and l_files or []:

            filex = open(files)
            tree = etree.parse(filex)
            read = tree.xpath('//record[@model="ir.ui.view"]')
            xpaths_list = []
            for line in read:
                inherit = t_search.lower() in ('module', 'all') and \
                    line.xpath('//field[@name="inherit_id"]') or\
                    []

                for tags in inherit:
                    name = tags.attrib.get('ref', False)
                    name = name and name.split('.')
                    name = name and name[0]
                    if name in mo_list:
                        filex.close()
                        return self.get_attr(line, 'xpath', 'expr')

                model = t_search.lower() in ('model', 'all') and \
                    line.xpath('//field[@name="model"]') or\
                    []

                for tags in model:
                    name = tags.text
                    if name in mo_list:
                        filex.close()
                        return self.get_attr(line, 'xpath', 'expr')

            filex.close()
            return False

    def modify_arch(self, l_files, types='a'):
        '''
        Modifie architecture view to use in openerp V7
        Remove depreciate values and add version description view
        @param l_files List with file path xml
        @param types Type change
               'a' Change all include xpath rute with relative way
               't' Basicaly change to work with V7 standard
               'x' Only change xpath route to use the realative way
        '''
        l_files = self.files or l_files and type(l_files) is list or \
            l_files and [l_files]

        for files in l_files:

            filex = open(files)
            tree = etree.parse(filex)
            read = tree.xpath('//record[@model="ir.ui.view"]')
            for line in read:
                inherit = types in ('a', 'x') and \
                    line.xpath('//field[@name="inherit_id"]')

                inherit and line.xpath('//xpath') and self.change_xpath(line)

                line.xpath('//field[@name="type"]') and \
                    self.remove_depreciated(line)
                line.xpath('//form') and self.version_7(line)

            out = open('%s' % files, 'w')
            tree.write(out, xml_declaration=True, encoding='UTF-8')
            out.close()

            return True

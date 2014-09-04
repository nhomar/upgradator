#!/usr/bin/env python
#-*- coding:utf-8 -*-
import os
#######################
# constants declaration
#######################


class migrateNextVersion():

    '''
    Create to prepare fields to migrate in V7 odoo
    Change the import and inherits method for run in the V7
    '''

    def __init__(self, l_files=None, version='7.0'):
        '''
        Maker to add list files and call for any method in this class
        @param l_files  List whit path for any file with python code to migrate

        '''
        self.version = '7.0'
        self.l_files = type(l_files) is list and l_files or l_files and \
            [l_files]

    def change_import_method(self, line):
        '''
        Change the method to import the necessary libraries for odoo modules
        @param line String with method import line

        '''
        text = line
        if line.find('from osv', 0, 8) >= 0:

            if 'fields' in line and line.find('osv', 8) < 0:
                text = 'from odoo.osv import fields, osv\n'

            elif line.find('osv', 8) > 0 and not 'fields' in line:
                text = ''

            elif 'fields' in line and line.find('osv', 8) > 0 and 'orm' \
                    not in line:
                text = 'from odoo.osv import osv, fields\n'

            elif 'fields' in line and line.find('osv', 8) > 0 and \
                 'orm' in line:
                text = 'from odoo.osv import osv, fields, orm\n'

        elif line.find('import netsvc', 0, 13) >= 0:
            text = 'import odoo.netsvc as netsvc\n'

        elif line.find('from tools.', 0, 13) >= 0:
            text = 'from odoo.tools%s\n' % line[10:]

        elif line.find('import tools', 0, 13) >= 0:
            text = 'import odoo.tools as tools\n'

        return text

    def change_inherits_class(self, line):
        '''
        Now we have a new method to inherit class from odoo this method
        change it
        @param line String with class definition line
        '''

        text = line

        if line.find('osv.osv') >= 0 and not 'osv_memory' in line:
            text = line.replace('osv.osv', 'osv.Model')

        elif line.find('osv.osv_memory') >= 0:
            text = line.replace('osv.osv_memory', 'osv.TransientModel')

        return text

    def main(self, files, change_type='a'):
        '''
        Process to read lines from files and change it if is necessary calling
        corresponding method
        @param files List or string with path for all .py files
        @param change_type Change type to script:
                           a: All change class definition and import method
                           cl: Change only class definition
                           im: Change only import method
        '''

        files = self.l_files or type(files) is list and files or [files]
        for one in files:
            open_f = open(one, 'rw')
            os.popen('touch clean')
            copy_f = open('clean', 'w')
            cn = False
            for line in open_f.readlines():
                text = line
                if line.find('import') >= 0 and \
                        change_type.lower() in ('a', 'im'):
                    text = self.change_import_method(line)

                if line.find('class') >= 0 and \
                        change_type.lower() in ('a', 'cl'):

                    cn = line[line.find(' '):line.find('(')].strip()

                    text = self.change_inherits_class(line)
                    cn = '%s%s' % (cn, '()')
                if cn and line.find(cn) >= 0:
                    text = ''
                    cn = False
                copy_f.write(text)
            os.rename('clean', '%s' % one)
            open_f.close()
            copy_f.close()

        return True

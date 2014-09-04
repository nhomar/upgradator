#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os

"""
A little lib where all particularities from one version to another will be
taken into account basically here you will find a set of "helper" methods to be
used as tools to include the correct elements on python files.
"""

class migrateNextVersion():
    '''Create to prepare fields to migrate in V7 openerp Change the import and
    inherits method for run in the V7 Object to set the enviroment elements to
    work with.

    :param list l_files: List with path for any file with python code to migrate
    :param str version: Version to migrate to.
    :returns: object

    '''

    def __init__(self, l_files=None, version='7.0'):
        self.version = '7.0'
        self.l_files = type(l_files) is list and l_files or l_files and \
            [l_files]

    def change_import_method(self, line):
        '''namespace openerp.* must be respected due to new framework way to work
        this method ensure the line which import osv respect those name space.

        >>> from upgrade_code import migrateNextVersion

        Set the python files in a list walking in the folder.

        >>> mnv = migrateNextVersion(['file1.py', 'file2.py'])

        If the import is not an Openerp ones they are simply ignored

        >>> mnv.change_import_method('import something')
        'import something'

        If it doesn't respect the namespace it is changed

        >>> mnv.change_import_method('from osv import fields, osv\\n')
        'from openerp.osv import osv, fields\\n'

        :param str line: with method import line

        '''
        text = line
        if line.find('from osv', 0, 8) >= 0:

            if 'fields' in line and line.find('osv', 8) < 0:
                text = 'from openerp.osv import fields, osv\n'

            elif line.find('osv', 8) > 0 and not 'fields' in line:
                text = ''

            elif 'fields' in line and line.find('osv', 8) > 0 and 'orm' \
                    not in line:
                text = 'from openerp.osv import osv, fields\n'

            elif 'fields' in line and line.find('osv', 8) > 0 and \
                 'orm' in line:
                text = 'from openerp.osv import osv, fields, orm\n'

        elif line.find('import netsvc', 0, 13) >= 0:
            text = 'import openerp.netsvc as netsvc\n'

        elif line.find('from tools.', 0, 13) >= 0:
            text = 'from openerp.tools%s\n' % line[10:]

        elif line.find('import tools', 0, 13) >= 0:
            text = 'import openerp.tools as tools\n'

        return text

    def change_inherits_class(self, line):
        '''Now we have a new method to inherit class from openerp this method
        change it and set new elements to classes

        :param str line: class definition
        '''

        text = line

        if line.find('osv.osv') >= 0 and not 'osv_memory' in line:
            text = line.replace('osv.osv', 'osv.Model')

        elif line.find('osv.osv_memory') >= 0:
            text = line.replace('osv.osv_memory', 'osv.TransientModel')

        return text

    def main(self, files, change_type='a'):
        '''Process to read lines from files and change it if is necessary calling
        corresponding method

        :param list files: List or string with path for all .py files
        :param str change_type: Change type to script 'a' All change class definition and import method 'cl' Change only class definition 'im' Change only import method
        :returns boolean
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

if __name__=='__main__':
    import doctest
    doctest.testmod()

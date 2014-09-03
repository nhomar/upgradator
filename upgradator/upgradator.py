#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
This Script can help you to verify the impact of migrate a module
from one version to another in terms of how much models you need to verify

It is specially usefull when you need to analyse a module in OpenERP or
Openerp Community and then, understand what you need to test,
even before install it.

If you have Technical Knowledge it can be used mixed with other script
to automigrate your module.

TODO: Auto apply pep8.
TODO: Modify what is obvious must be modified.
'''

import os
import commands

def main(path, ext, migrate, view):
    '''
    Walk trought a folder and count lines with python code and some other
    features
    :path: Absolute or relative path where the module is.
    :ext: File to test, .xml .py .yml
    '''
    counter = {
        'classes': [],
        'inherited': [],
        'views': [],
        'action': [],
        'menus': [],
        'groups': [],
        'new_field': [],
        'commented': [],
        'n_commented': [],
        'inherited_field': [],
        'pep': [],
        'pep_solved': [],
        'pep_n_solved': [],
        'rules': [],
        'create': [],
        'write': [],
        'search': [],
        'mistake_view': [],
        'unlink': [],
        'def': [],
        'workflow': [],
        'report': [],
        'author': [],
    }
    for root, dirs, files in os.walk(path):
        for filei in [f for f in files if f.lower().endswith(ext)]:
            completepath = os.path.join(root, filei)
            if migrate and '.py' in filei:
                print "TODO"
                #migrate.main(completepath, args.migrate)
            script = open(completepath)
            scripts = script.read()
            script.close()
            if filei == "__openerp__.py":
                author = get_author(scripts)
                counter['author'].append(author)
            if '.py' in filei and not 'openerp' in filei and not \
                    'init' in filei:

                check = check_pep(completepath)
                check and counter['pep'].append(filei)
                # TODO: if args.pep and check:
                if True:
                    check = apply_pep(completepath)
                    check and \
                        counter['pep_n_solved'].append(filei) or not \
                        check and counter['pep_solved'].append(filei)
            if completepath.endswith('.xml') and view:
                depreciated_view = False
                depreciated_view = view.search_model(completepath,
                                                     'all',
                                                     ['res.partner.address'])
                if view:
                    #TODO view.modify_arch(completepath, args.views)
                    print "view.modify_arch(completepath, args.views)"

                    if depreciated_view:
                        counter['mistake_view'].append(depreciated_view)
                        depreciated_view = False

            lines = scripts.split('\n')
            for i in lines:
                if completepath.endswith('.py'):
                    if is_class(i):
                        counter['classes'].append(i)
                    if is_field(i):
                        counter['new_field'].append(i)
                        cm = has_comment(i, 'field')
                        cm and \
                            counter['commented'].append(i) or not \
                            cm and counter['n_commented'].append(i)
                    if is_method(i):
                        counter['def'].append(i)
                    if is_create(i):
                        counter['create'].append(i)
                    if is_write(i):
                        counter['write'].append(i)
                    if is_unlink(i):
                        counter['unlink'].append(i)
                    inh = is_inherited(i)
                    if inh:
                        counter['inherited'].append(inh)

                if completepath.endswith('.xml'):

                    if is_view(i):
                        counter['views'].append(i)
                    if is_workflow(i):
                        counter['workflow'].append(i)
                    if is_report(i):
                        counter['report'].append(i)
                    if is_action(i):
                        counter['action'].append(i)
                    if is_menu(i):
                        counter['menus'].append(i)
                    if is_group(i):
                        counter['groups'].append(i)
                if ext == '.csv':
                    if is_isrule(i):
                        counter['rules'].append(i)
    return counter


def has_comment(string, tp=None):
    '''
    Verify if the field or method have their help and comment
    '''
    if tp == 'field':
        return string.find('help') >= 0 and True or False
    return False


def get_author(filer):
    dic = eval(filer)
    author = dic.get('author')
    return author


def is_method(lineofcode):
    if lineofcode.startswith("    def "):
        return True
    return False


def check_pep(files=None):
    '''
    Check if apply pep 8 style in your files
    you can send the files or use the define in the maiker
    '''

    check = files and \
        commands.getoutput('''
                     pep8 %s ''' % files)

    return check and True or False


def apply_pep(files=None):
    '''
    Apply pep 8 style in your files
    you can send the files or use the define in the maiker
    '''

    files and \
        commands.getoutput('''
                     autopep8 -i %s ''' % files)

    return check_pep(files)


def is_create(lineofcode):
    if lineofcode.startswith("    def create"):
        return True
    return False


def is_write(lineofcode):
    if lineofcode.startswith("    def write"):
        return True
    return False


def is_unlink(lineofcode):
    if lineofcode.startswith("    def unlink"):
        return True
    return False


def is_workflow(lineofcode):
    if lineofcode.find("workflow.transition") > 0:
        return True
    if lineofcode.find("workflow.activity") > 0:
        return True
    return False


def is_report(lineofcode):
    if lineofcode.find("<report") > 0:
        return True
    return False


def is_class(lineofcode):
    '''
    Lines with
    python code that touch a class
    '''
    if lineofcode.startswith('class'):
        return True
    return False


def is_inherited(lineofcode):
    '''
    Lines with
    python code inherited from original models
    '''
    if lineofcode.find('inherit') > 0:
        _global = lineofcode.strip().split('=')
        if len(_global) > 1:
            res = _global[1].strip().\
                replace('\'', '').replace('"', '')
            return res
    return False


def is_action(lineofcode):
    '''
    Line with xml code with an action
    '''
    if lineofcode.find('ir.actions.act_window') > 0:
        return True
    return False


def is_menu(lineofcode):
    '''
    Line with xml code with a menu
    '''
    if lineofcode.find('menuitem') > 0:
        return True
    return False


def is_view(lineofcode):
    '''
    Line with xml code with a view
    '''
    if lineofcode.find('ir.ui.view') > 0:
        return True
    return False


def is_group(lineofcode):
    '''
    Line with xml code with a group
    '''
    if lineofcode.find('res.groups') > 0:
        return True
    return False


def is_isrule(lineofcode):
    '''
    Line with xml code with a menu
    '''
    if len(lineofcode.split(',')) > 4:
        return True
    return False


def is_field(lineofcode):
    '''
    Line with an openerp new field
    '''
    if lineofcode.find('fields.') > 0:
        return True
    return False


if __name__ == "__main__":
    print "upgradator"

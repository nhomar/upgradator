#!/usr/bin/env python
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
import logging
import argparse
import commands
import migrate_V7
import migrate_view

parser = argparse.ArgumentParser(
    description='This Script can help you to verify the impact of migrate a module')
parser.add_argument('-p', '--path', required=True, help='Path where are the modules to verify')
parser.add_argument('-v', '--views', required=False, help='''
                     Use if you want migrate view to next version
                     Use 'a' if you want change all to view
                     Use 't' Basicaly change to work with V7 standard
                     Use 'x' Only change xpath route to use the realative way''')
parser.add_argument('-m', '--migrate', required=False, help='''
                     Use if you want migrate import method and class definition .
                     Use 'a' if you want change all to import
                     Use 'cl' if you want change only class definition
                     Use 'im' if you want change only import definition''')
parser.add_argument('-P', '--pep', action="store_true", required=False,
                    help='Use if you want apply pep8 in all files with python code. To use this option you need install pep8 and autopep8 libraries')
args = parser.parse_args()

if args.pep:
    try:
        import pep8
        import autopep8
    except:
        logging.warning(
            'To check and apply pep8 style you need install the libraries pep8 and autopep8 sudo pip install pep8 autopep8 ')


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
                migrate.main(completepath, args.migrate)
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
                if args.pep and check:
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
                    view.modify_arch(completepath, args.views)

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

    path_to_explore = args.path
    migrate = False
    view = False
    if args.migrate:
        migrate = migrate_V7.migrate_next_version()
    if args.views:
        view = migrate_view.migrate_view()
    tof = ['.xml', '.py', '.csv']
    result = [main(path_to_explore, t, migrate, view) for t in tof]
    logging.getLogger().setLevel(logging.INFO)
    logging.info("Description, %s" % ("Total Elements"))
    logging.info("Total New Classes, %s" % len(result[1].get('classes')))
    different = len(list(set(result[1].get('inherited'))))
    different and \
        logging.info("Total Inherited Classes, %s" % different)
    result[1].get('def') and \
        logging.info("Total Methods, %s" % len(result[1].get('def')))
    result[1].get('pep') and \
        logging.warning("Total of pep8 mistakes, %s" % len(result[1].get('pep')))
    result[1].get('pep_solved') and \
        logging.info("Total of pep8 apply, %s" % len(result[1].get('pep_solved')))
    result[1].get('pep_n_solved') and \
        logging.warning("Total of pep8 not apply because you need do it manualy, %s" %
                        len(result[1].get('pep_n_solved')))
    result[1].get('create') and \
        logging.info("Total Create, %s" % len(result[1].get('create')))
    result[1].get('write') and \
        logging.info("Total Write, %s" % len(result[1].get('write')))
    result[1].get('unlink') and \
        logging.info("Total Unlink, %s" % len(result[1].get('unlink')))
    result[1].get('new_field') and \
        logging.info("Total New Fields, %s" % len(result[1].get('new_field')))
    result[1].get('commented') and \
        logging.info("Total fields with helps, %s" % len(result[1].get('commented')))
    result[1].get('n_commented') and \
        logging.info("Total fields without helps, %s" % len(result[1].get('n_commented')))
    result[0].get('views') and \
        logging.info("Total Views,  %s" % len(result[0].get('views')))
    result[0].get('action') and \
        logging.info("Total Actions,  %s" % len(result[0].get('action')))
    result[0].get('menus') and \
        logging.info("Total Menus,  %s" % len(result[0].get('menus')))
    result[0].get('workflow') and \
        logging.info("Total Workflow,  %s" % len(result[0].get('workflow')))
    result[0].get('mistake_view') and \
        logging.warning("Total depreciated views, %s" %
                        len(result[0].get('mistake_view')))
    result[0].get('report') and \
        logging.info("Total Reports,  %s" % len(result[0].get('report')))
    result[0].get('groups') and \
        logging.info("Total Groups,  %s" % len(result[0].get('groups')))
    result[2].get('rules') and \
        logging.info("Total Rules,  %s" % len(result[2].get('rules')))
    logging.info("Total authors,  %s" %
                 str(len(set(result[1].get('author')))))

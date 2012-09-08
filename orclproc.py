#! /usr/bin/python
# coding: utf-8

import sys
import os
import optparse

__author__ = 'brainfs/yatt'
__version__ = '0.0.1'
__license__ = 'MIT'

# sample
# $ python orclproc.py user/pass@sid
# $ python orclproc.py user/pass@sid proc_X
# $ python orclproc.py -e Japanese_Japan.AL32UTF8 user/pass@sid 

def dump(setting):
    # setting contains:
    #   profile  string  connection profile
    #   oracle   string  Oracle version
    if setting['oracle'] == '10g':
        import cx_Oracle
    else: # 11g
        import cx_Oracle

    # set encoding
    if setting['encoding']:
        os.environ['NLS_LANG'] = setting['encoding']

    # switch mode to binary on windows
    if sys.platform == "win32":
        import msvcrt
        msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)

    with cx_Oracle.connect(setting['profile']) as conn:
        q = """
select 
    OBJECT_NAME,
    dbms_metadata.get_ddl(OBJECT_TYPE, OBJECT_NAME)
from
    user_procedures
"""
        if setting['entries']:
            quoted = map(lambda n: "'%s'" % n.upper(), setting['entries'])
            q += "where object_name in (%s)" % ','.join(quoted)
        
        for row in conn.cursor().execute(q):
            print row[0]
            # http://cx-oracle.sourceforge.net/html/lob.html
            print row[1].read()

def main():
    from optparse import OptionParser
    
    setting = {
        'profile': None,
        'oracle': None,
    }

    parser = optparse.OptionParser(
        usage='%prog user/password[@host] procedure_or_function_names+',
        version='%prog ' + __version__
        )
    
    parser.add_option('-o', '--oracle', dest='version', help='specify oracle version', type='choice', choices=['10g', '11g'], default='11g')

    #
    parser.add_option('-e', '--encoding', dest='encoding', help='client encoding')
    
    (options, args) = parser.parse_args()
    
    if len(args) < 1:
        parser.print_help()
        return
    
    # overwrite by argument
    setting['profile'] = args[0]
    setting['entries'] = args[1:]
    setting['oracle']  = options.version
    #
    setting['encoding'] = options.encoding
    
    try:
        dump(setting)
    except Exception, e:
        print 'ERROR:',e
    

if __name__ == '__main__':
    main()

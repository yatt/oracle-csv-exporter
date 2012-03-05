#! /usr/bin/python
# coding: utf-8

################################################################################
#
# CSV file export program for Oracle 10g/11g
#
#        this program can handle query properly if query response contain very
#    large amount of content and generated csv size become also large.
#        csv format program generate is costomizable. see list below
#
#            - specify newline character code CR / LF / CRLF
#            - enclose each column by double-quote
#
#
#    
# sample:
#
# # simple
# $ orclexporter user/pass@host 'select * from tbl'
# # load sql file
# $ orclexporter user/pass@host @program.sql
# # oracle version specified
# $ orclexporter --oracle=10g user/pass@host 'select * from tbl'
# # enclose each column by "
# $ orclexporter -q user/pass@host 'select * from tbl'
# # specify line separator
# $ orclexporter -newline=CRLF user/pass@host 'select * from tbl'
#
################################################################################

import sys
import os
import optparse
import csv

__author__ = 'brainfs/yatt'
__version__ = '0.0.1'
__license__ = 'MIT'



def dump(setting):
    #
    # setting contains:
    #   profile  string  connection profile
    #   query    string  sql statement
    #   oracle   string  Oracle version
    #   quote    boolean enclose each field by double quote or not
    #   newline  string  line separator (CR, LF, CRLF)
    #
    dialect = {
        'quoting': csv.QUOTE_ALL if setting['quote'] else csv.QUOTE_NONE,
        'lineterminator': {'CR':'\r', 'LF':'\n',  'CRLF':'\r\n'}[setting['newline']],
    }
    
    # TODO: switch oracl version
    if setting['oracle'] == '10g':
        import cx_Oracle
    else: # 11g
        import cx_Oracle

    # switch mode to binary on windows
    if sys.platform == "win32":
        import os, msvcrt
        msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)

    writer = csv.writer(sys.stdout, **dialect)
    with cx_Oracle.connect(setting['profile']) as conn:
        for row in conn.cursor().execute(setting['query']):
            writer.writerow(row)

def main():
    from optparse import OptionParser
    
    setting = {
        'profile': None,
        'query': None,
        'quote': False,
        'oracle': None,
        'linesep': None,
    }

    parser = optparse.OptionParser(
        usage='%prog user/password[@host] (sql statement|@script)',
        version='%prog ' + __version__
        )
    
    parser.add_option('-q', action='store_true', dest='quote', help='enclose each field by double quote (")', default=False)
    parser.add_option('-n', '--newline', dest='newline', help='specify line separator CR / LF / CRLF', type='choice', choices=['CR', 'LF', 'CRLF'], default='CRLF')
    parser.add_option('-o', '--oracle', dest='version', help='specify oracle version', type='choice', choices=['10g', '11g'], default='11g')
    
    (options, args) = parser.parse_args()
    
    if len(args) != 2:
        parser.print_help()
        return
    
    # overwrite by argument
    setting['profile'] = args[0]
    setting['query']   = args[1]
    setting['quote']   = options.quote
    setting['newline'] = options.newline
    setting['oracle']  = options.version
    
    # read sql file if argument 'statement' is prefixed by '@' (ex. @foo.sql
    if setting['query'][0] == '@':
        script = setting['query'][1:]
        if not os.path.exists(script):
            print 'error: no such sql file:',script
            return
        setting['query'] = open(script).read()
    
    try:
        dump(setting)
    except Exception, e:
        print 'ERROR:',e
    

if __name__ == '__main__':
    main()

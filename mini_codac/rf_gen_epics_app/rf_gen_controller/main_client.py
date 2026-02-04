#!/usr/bin/env python3

from tcp_client import tcp_client

import argparse

"""
Created on Wed Apr12 10:53:55 2023

@author: Luke Cota

PURPOSE:
   Short description here

INPUTS:
   List all inputs here

OUTPUTS:
   NONE

DEPENDENCIES:
   NONE

NOTES:
   Some notes here

   VARIABLES (Important non IO variables_):      NONE
"""
def main():
    descript = '''Application description here'''
    ip_help  = '''Ip address of tcp server'''
    prt_help = '''Port upon which the server is listening'''
    #opt_help = '''Description of option here'''
    #opno_help = '''Description of option with no arguments'''

    parser = argparse.ArgumentParser(description = descript)
    parser.add_argument('IP', help = ip_help)
    parser.add_argument('PORT', help = prt_help)
    #parser.add_argument('-o', '--opt', help = opt_help, metavar = 'opt_display_name')
    #parser.add_argument('-n', '--no', help = opno_help, action = 'store_true',
    #                    default = False)

    # Create list of keys to the args dictionary
    args = parser.parse_args().__dict__

    tcp_client(args['IP'], args['PORT'])

    return

######################################### main ###########################################
if (__name__ == '__main__'):
    main()


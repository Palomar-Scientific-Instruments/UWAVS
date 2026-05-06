#!/usr/bin/env python3

import argparse

def crss_ref(sig_csv, fbs_csv):
    return

def main():
    descript = '''Application description here'''
    sig_help = '''Path to csv file containing components from Signals and Components'''
    fbs_help = '''Path to csv file containing COTS tab from FBS'''
    opno_help = '''Description of option with no arguments'''

    parser = argparse.ArgumentParser(description = descript)
    parser.add_argument('SIGS', help = sig_help)
    parser.add_argument('FBS', help = fbs_help)
#    parser.add_argument('-o', '--opt', help = opt_help, metavar = 'opt_display_name')
#    parser.add_argument('-n', '--no', help = opno_help, action = 'store_true',
#                        default = False)

    # Create list of keys to the args dictionary
    args = parser.parse_args().__dict__

    sig_csv = args['SIGS']
    fbs_csv = args['FBS']

    cross_ref(sig_csv, fbs_csv)

    return

######################################### main ###########################################
if (__name__ == '__main__'):
    main()


#!/usr/bin/env python3.11

from tcp_server import tcp_server

import argparse

def main():
    descript = '''Driver for RF Generator'''
    ip_help  = '''Ip address of host'''
    prt_help = '''Port number upon which the server will be listening'''
    log_help = '''Use this option to create a debugging log file.'''

    parser = argparse.ArgumentParser(description = descript)
    parser.add_argument('IP', help = ip_help)
    parser.add_argument('PORT', help = prt_help)
    parser.add_argument('-l', '--LOG', help = log_help, action = 'store_true',
                        default = False)

    # Create list of keys to the args dictionary
    args = parser.parse_args().__dict__

    tcp_server(args['IP'], args['PORT'], args['LOG'])

    return

######################################### main ###########################################
if (__name__ == '__main__'):
    main()




















#!/usr/bin/env python3

import argparse

from modbus_client import Modbus_Client
from rf_gen_controller import (get_forward_power,
                               get_control_source,
                               get_date,
                               get_domain,
                               get_hostname,
                               get_ip,
                               get_match_mode,
                               get_phase,
                               get_power,
                               get_state,
                               get_reflected_power,
                               get_load_cap,
                               get_tune_cap,
                               rf_on, rf_off,
                               set_load_cap,
                               set_match_mode,
                               set_power,
                               set_tune_cap)

def get_ip_address():
    print(f'Current IP addr: {get_ip()}')
    return

def get_date_time():
    print(f'{get_date()}')
    return

def get_hostname_please():
    print(f'Hostname: {get_hostname()}')
    return

def get_domain_please():
    print(f'Domain name: {get_domain()}')
    return

def get_ctrl_src():
    print(f'Current ctrl source: {get_control_source()}')
    return

def please_get_state():
    print(f'Current state: {get_state()}')
    return

def get_power_set_point():
    print(f'Power set to: {get_power()}')
    return

def set_power_set_point(set_point: str):
    try:
        power = int(set_point)
    except ValueError:
        print(f'ERROR: Invalid value ({set_point}. Argument must be an integer')
        return

    set_power(power)
    get_power_set_point()

    return

def turn_rf_on():
    rf_on()
    return

def turn_rf_off():
    rf_off()
    return

def forward_power_please():
    print(f'Forward power: {get_forward_power()}')
    return

def reflected_power_please():
    print(f'Reflected power: {get_reflected_power()}')
    return

def read_tune_cap_please():
    print(f'Tune cap (%): {get_tune_cap()}')
    return

def read_load_cap_please():
    print(f'Load cap (%): {get_load_cap()}')
    return

def set_load_cap_please(pos):
    try:
        cap_pos = int(pos)
    except ValueError:
        print(f'ERROR: Invalid value ({pos}. Argument must be an integer')
        return

    read_load_cap_please()
    set_load_cap(cap_pos)
    read_load_cap_please()

    return

def get_match_mode_now():
    print(f'Match mode: {get_match_mode()}')
    return

def get_phase_now():
    print(f'The current phase is {get_phase()}')
    return

def set_match_mode_now(m_mode):
    try:
        mode = int(m_mode)
        if ((mode < 1) or (mode > 2)):
            print(f'ERROR: The match mode should be either 1 or 2. Yours {mode}')
            return
    except ValueError:
        print(f'ERROR: Invalid value ({m_mode}. Argument must be an integer')
        return

    set_match_mode(mode)

    return

def main():
    descript = '''Controler for the Cito Plus RF Generator'''
    arg_help = '''General input, ussually an argument corresponding to a given
                  option'''
    snd_help = '''Sends command to user Modbus command to RF generator. The 
                  "arg" to this command should be the message that is to be
                  sent to the generator'''
    adr_help = '''Get/Set the IP address. In order to get the current IP
                  address give the sring "get" as an argument. To set the IP
                  address give the new IP as the argument'''
    pwr_help = '''Get/Set the Power Set Point of the RF Generator. To get the
                  current set point give the string "get" as an argument (arg).
                  In order to set the Power Set Point give the new value as the
                  argument (arg).'''
    ctl_help = '''Get/Set the control source for the RF Generator. To get the
                  control source give the string "get" as the argument (arg).
                  When setting the control source give one of the source codes
                  as an argument: 0=Each, 1=Front panel, 2=Modbus-TCP,
                  3=Modbus-RTU, 4=Analog Port, 5=Fieldbus'''
    dte_help = '''Gets the Current date and time from the RF Generator'''
    ste_help = '''Gets the current state of the RF Generator. See the "Air
                  Cooled RF Generator cito and cito Plus" user manual for a
                  description of the state codes'''
    rfd_help = '''Turn the RF Generator off.'''
    rfu_help = '''Turn the RF Generator on.'''
    fwp_help = '''Gets the forward power'''
    rfp_help = '''Gets the reflected power'''
    tcp_help = '''Gets the tune cap position (units are %)'''
    lcp_help = '''Gets the load cap position (units are %)'''
    stp_help = '''Sets the tune cap position'''
    slp_help = '''Sets the load cap position'''
    mth_help = '''Get/Set the match mode for the RF Generator. To get the
                  match mode give the string "get" as the argument (arg).
                  When setting the match mode give either 1 for "Manual" or
                  2 for "Automatic"'''
    hsn_help = '''Gets the host name of the RF Generator'''
    pha_help = '''Get the phase of the RF Generator'''

    parser = argparse.ArgumentParser(description = descript)
#    parser.add_argument('arg', help = arg_help)
#    parser.add_argument('-o', '--opt', help = opt_help, metavar = 'opt_display_name')
    parser.add_argument('-c', '--ctrl_src', help = ctl_help, action = 'store_true',
                        default = False)
    parser.add_argument('-d', '--date', help = dte_help, action = 'store_true',
                        default = False)
    parser.add_argument('-dn', '--domain', help = dte_help, action = 'store_true',
                        default = False)
    parser.add_argument('-fp', '--fwd_pwr', help = rfd_help, action = 'store_true',
                        default = False)
    parser.add_argument('-i', '--ip_addr', help = adr_help)
    parser.add_argument('-m', '--match', help = mth_help)
    parser.add_argument('-n', '--hostname', help = hsn_help, action = 'store_true',
                        default = False)
    parser.add_argument('-p', '--power', help = pwr_help)
    parser.add_argument('-rfd', '--rf_off', help = rfd_help, action = 'store_true',
                        default = False)
    parser.add_argument('-rfu', '--rf_on', help = rfd_help, action = 'store_true',
                        default = False)
    parser.add_argument('-rp', '--rfl_pwr', help = rfd_help, action = 'store_true',
                        default = False)
    parser.add_argument('-s', '--state', help = ste_help, action = 'store_true',
                        default = False)
    parser.add_argument('-tcp', '--rd_tc', help = rfd_help, action = 'store_true',
                        default = False)
    parser.add_argument('-lcp', '--rd_lc', help = rfd_help, action = 'store_true',
                        default = False)
    parser.add_argument('-stc', '--set_tc', help = rfd_help)
    parser.add_argument('-slc', '--set_lc', help = rfd_help)
    parser.add_argument('-ph', '--phase', help = rfd_help, action = 'store_true',
                        default = False)
    
    # Create list of keys to the args dictionary
    args = parser.parse_args().__dict__

    if (args['ip_addr'] == 'get'):
        get_ip_address()
        return
    elif (args['ip_addr']) != None:
        set_ip_address(args['ip_addr'])
        return

    if (args['power'] == 'get'):
        get_power_set_point()
        return
    elif (args['power'] != None):
        set_power_set_point(args['power'])
        return

    if (args['match'] == 'get'):
        get_match_mode_now()
        return
    elif (args['match'] != None):
        set_match_mode_now(args['match'])
        return

    if (args['ctrl_src']):
        get_ctrl_src()
        return

    if (args['hostname']):
        get_hostname_please()
        return

    if (args['domain']):
        get_domain_please()
        return

    if (args['date']):
        get_date_time()
        return

    if (args['state']):
        please_get_state()
        return

    if (args['rf_off']):
        turn_rf_off()
        return

    if (args['rf_on']):
        turn_rf_on()
        return

    if (args['fwd_pwr']):
        forward_power_please()
        return

    if (args['rfl_pwr']):
        reflected_power_please()
        return

    if (args['rd_tc']):
        read_tune_cap_please()
        return

    if (args['rd_lc']):
        read_load_cap_please()
        return

    if (args['set_lc'] != None):
        set_load_cap_please(args['set_lc'])
        return

    if (args['match']):
        return

    if (args['phase']):
        get_phase_now()
        return

    return

######################################### main ###########################################
if (__name__ == '__main__'):
    main()















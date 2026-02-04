
import struct

from modbus_client import Modbus_Client
from parameters    import CMDS, MAX_POWER, MIN_POWER
from psi_message   import Psi_Message

def _read_param(param: str) -> str|int:
    """
    Reads a parameter value from the RF Generator

    Inputs:
        param (str) - Name of parameter to be read. This will be the key to the
                      CMD dict in the parameters.py file. Use the "list_params"
                      function to get a list of the keys in the CMD dict
    """
    func_id = f'{__name__}._read_param'
    pmsg = Psi_Message()

    if (param not in CMDS.keys()):
        pmsg.error(func_id, f'No such command found ({param})')
        return None

    mbc = Modbus_Client()
    snd_cmd = mbc.build_mb_cmd(CMDS[param][0], 'r')
    resp_data = mbc.send_cmd(snd_cmd, 'r')

    if (CMDS[param][1] == "int"):
        ret_val = struct.unpack('>i', resp_data)

    elif (CMDS[param][1] == "str"):
        ret_val = resp_data.decode("utf-8")

    else:
        ret_val = resp_data

    return ret_val

def _set_param(param: str, value: int):
    """
    Sets the value of a parameter in the RF Generator

    Inputs:
        param (str) - Name of parameter to be read. This will be the key to the
                      CMD dict in the parameters.py file. Use the "list_params"
                      function to get a list of the keys in the CMD dict
        value (int) - Value to which the prameter will be set
    """
    mbc = Modbus_Client()
    snd_cmd = mbc.build_mb_cmd(CMDS[param][0], 'w', value)
    resp_data = mbc.send_cmd(snd_cmd, 'w')

    return

def get_ip() -> str:
    """
    Gets the Current IP addres of the Modbus server
    """
    func_id = f'{__name__}.get_ip'
    pmsg = Psi_Message()

    raw_ip = _read_param('get_ip')
    ip_addr = f'{raw_ip[0]}.{raw_ip[1]}.{raw_ip[2]}.{raw_ip[3]}'

    return ip_addr

def get_date() -> str:
    """
    Retrieves the current date on the RF generator
    """
    date_cur = _read_param('get_date')
    return date_cur

def get_domain() -> str:
    """
    Retrieves the domain name of the RF Generator
    """
    domain_name = _read_param('domain_name')
    return domain_name

def get_hostname() -> str:
    """
    Retrieves the host name of the RF Generator
    """
    host_name = _read_param('hostname')
    return host_name

def get_power() -> int:
    """
    Retrieves the current set point for the power in mili Watts
    """
    power = _read_param('power_set_point')
    return power[0]

def get_state() -> int:
    state = _read_param('state')
    return state[0]

def get_control_source() -> int:
    ctrl_src = _read_param('ctrl_src')
    return ctrl_src[0]

def get_forward_power() -> int:
    fwd_pwr = _read_param('fwd_pwr')
    return fwd_pwr[0]

def get_reflected_power() -> int:
    rfl_pwr = _read_param('rfl_pwr')
    return rfl_pwr[0]

def get_match_mode() -> int:
    match_mode = _read_param('match_mode')
    return match_mode[0]

def get_load_cap() -> int:
    """
    Get load capacitor position. Returns an integer in the range 0 -> 1000. A
    value of 1000 corresponds to 100.0%
    """
    lc_pos = _read_param('read_load_cap')
    return lc_pos[0]

def get_tune_cap() -> int:
    """
    Get tune capacitor position. Returns an integer in the range 0 -> 1000. A
    value of 1000 corresponds to 100.0%
    """
    tc_pos = _read_param('read_tune_cap')
    return tc_pos[0]

def get_phase() -> int:
    phase = _read_param('phase_shift')
    return phase[0]

def set_power(set_point: int):
    """
    Sets the RF Generator's power set point

    Inputs:
        set_point (int) - Set point of the RF Generator in mili-Watts. Note, the
                          minimum value is 1000 = 1W, and the maximum value is
                          1000000 = 1000W
    """
    func_id = f'{__name__}.set_power'
    pmsg = Psi_Message()

    power = set_point
    if (set_point < MIN_POWER): power = MIN_POWER
    if (set_point > MAX_POWER): power = MAX_POWER

    ret_val = _set_param('power_set_point', set_point)
    pmsg.debug(func_id, f'set_point return value is {ret_val}')
    return

def rf_on():
    """
    Turn Rf power on
    """
    _set_param('rf', 1)
    return

def rf_off():
    """
    Turn Rf power off
    """
    _set_param('rf', 0)
    return

def set_load_cap(cap_pos: int):
    """
    Sets the position of the load capacitor

    Inputs:
        cap_pos (int) - Position of the load capacitor. cap_pos = 1000 is 100.0%,
                        cap_pos = 0 is 0.0%
    """
    _set_param('move_load_cap', cap_pos)
    return

def set_tune_cap(cap_pos: int):
    """
    Sets the position of the tune capacitor

    Inputs:
        cap_pos (int) - Position of the tune capacitor. cap_pos = 1000 is 100.0%,
                        cap_pos = 0 is 0.0%
    """
    _set_param('move_tune_cap', cap_pos)
    return

def set_match_mode(m_mode):
    """
    Sets the match mode..

    Input:
        m_mode (int) - Match mode. Set m_mode = 1 for manual, and m_mode = 2
                       for auto
    """
    _set_param('match_mode', m_mode)
    return










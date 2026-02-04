
# As commands are added you must add a corresponding function, then add a
# key-value pair to the lookup dict (self._lookup). Where the key is the command
# and the value is the function that executes the command.

import socket

from numpy.random      import randint
from psi_message       import Psi_Message
from rf_gen_controller import (get_control_source, get_forward_power, get_ip,
                               get_load_cap, get_match_mode, get_phase,
                               get_power, get_reflected_power, get_state,
                               get_tune_cap, set_power)
                               

class Cmd_Lookup():
    """
    Lookup table.
    """

    def __init__(self):
        """
        Initializes the Cmd_Lookup class.

        Inputs:
            None
        """
        self._addr   = None
        self._ipmode = None

        self._lookup = {
                #                        'IPADDR?'  : self.get_ipaddr,
                        'IPADDR?'  : get_ip,
                        'IPMODE?'  : self.get_ipmode,
                        'HOSTNAME?': self.get_hostname,
                        'GETPOWER?' : get_power,
                        'GETSTATE?' : get_state,
                        'GETCTRLSRC?' : get_control_source,
                        'GETFWDPWR?'  : get_forward_power,
                        'GETRFLPWR?'  : get_reflected_power,
                        'GETMATCHMODE?' : get_match_mode,
                        'GETLDCAP?'     : get_load_cap,
                        'GETTNCAP?'     : get_tune_cap,
                        'GETPHASE?'     : get_phase,
                        'SETPOWER$'     : self.power_set
                       }

        return

    def cmd_lookup(self, cmd: str, args: str|int=None) -> str|int:
        """
        Wrapper function for the command lookup table.

        Inputs:
            cmd (str)      - Command which is a key in the lookup table. This key
                             corresponds to a value which is a function.
            args (str|int) - Optional argument that may accompany a command

        Returns:
            A sring which is the output of the function that is associated with
            the command key (cmd).
        """
        func_id = f'{__name__}.cmd_lookup'
        pmsg = Psi_Message()

        pmsg.debug(func_id, f'cmd={cmd}, args={args}')

        if (args != None):
            try:
                idx = cmd.find("$")
                cmd = cmd[:idx+1]
                rf_cmd = self._lookup[cmd](args)
            except KeyError:
                pmsg.error(func_id, f'Errr: "{cmd}" is an invalid command')
                rf_cmd = f'Error: "{cmd} is an invalid command'
        else:
            try:
                rf_cmd = self._lookup[cmd]()
            except KeyError:
                rf_cmd = f'Error: "{cmd} is an invalid command'

        return rf_cmd

    def get_ipaddr(self) -> str:
        """
        Returns the current IP address.

        Inputs:
            None
        """
        return get_ip()

    def get_ipmode(self) -> int:
        """
        Returns the current IP mode.

        Inputs:
            None
        """
#        return f'{randint(0, 10)}'
        return f'{randint(0, 10)}'

    def get_hostname(self):
        """
        Returns the hostname.

        Inputs:
            None
        """
        return socket.gethostname()

    def power_set(self, sp_power: str):
        """
        Sets the power set point

        Inputs:
            power (str) - Integer between 6000 and 0, which represents
                          the power to which the RF generator will be
                          set (in mW)
        """
        func_id = f'{__name__}.power_set'
        pmsg = Psi_Message()

        pmsg.debug(func_id, f'sp_power={sp_power}')

        try:
            power = int(sp_power)
        except ValueError as exc:
            try:
                power = int(sp_power[0])
                idx = sp_power.find("\n")
                if (idx < 0):
                    pmsg.error(func_id, f'Invalid value ({sp_power}) given for argument')
                    return

                power = int(sp_power[:idx+1])
                pmsg.debug(func_id, f'power={power}')
            except ValueError:
                pmsg.error(func_id, f'{exc}')
                return

        set_power(power)

        return
























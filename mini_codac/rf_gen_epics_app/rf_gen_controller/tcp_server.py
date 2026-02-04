
import socket
import numpy as np

from cmd_lookup   import Cmd_Lookup
from numpy.random import randint
from psi_message  import Psi_Message

CHUNK = 1024

def tcp_server(host_ip: str, port: int, bug_level: bool=None):
    """
    TCP server that takes in commands, and parses them using a lookup table. See
    cmd_lookup.py for the lookup table.

    Inputs:
        host_ip   (str)      - IP address of the server
        port      (int)      - Port number upon which the server is listening
        bug_level (opt, int) - Logging level. Set to True for creating a debug
                               log file. Otherwise a log file will only be
                               written to if there is a critical error.
    """
    func_id = f'{__name__}.tcp_server'
    pmsg = Psi_Message()

    cmd_table = Cmd_Lookup()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((host_ip, int(port)))
        sock.listen()

        while True:
            conn, addr = sock.accept()
            print(f'Connected to {addr[0]}, on port {addr[1]}')

            with conn:
                while True:
                    data = conn.recv(CHUNK)
                    
                    if not data:
                        break
                    
                    cli_msg = data.decode("utf-8")
                    cli_msg = cli_msg.strip()
                    cli_msg_list = cli_msg.split("\n")

                    idx = 0
                    for line in cli_msg_list:
                        if (line.find('$') >= 0):
                            cmd_arg = line.split("$")[1].strip()
                            try:
                                cmd_arg = int(cmd_arg)
                            except ValueError:
                                cmd_arg = str(cmd_arg)

                            cmd_table.cmd_lookup(cli_msg, args=cmd_arg)
                            pmsg.debug(func_id, f'({idx}) client msg: {line}, args: {cmd_arg}')

                        else:
                            snd_data = str(cmd_table.cmd_lookup(line))

                            pmsg.debug(func_id, f'({idx}) client msg: {line}, server resp: {snd_data}')
                            conn.sendall(snd_data.encode("utf-8"))

                        idx += 1

    return

























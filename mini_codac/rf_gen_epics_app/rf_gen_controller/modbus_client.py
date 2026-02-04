
import struct

from parameters      import (CMDS,
                             DEFAULT_IP_ADDR,
                             DEFAULT_TCP_PORT)
from psi_message     import Psi_Message
from pymodbus.client import ModbusTcpClient

class Modbus_Client(ModbusTcpClient):

    def __init__(self, ipaddr: str=None, tcp_port: int=None):
        """
        Initializes the Modbus_Client
        
        Inputs:
           ipaddr   (optional, str) - Current IP address of the Modbus server
           tcp_port (optional, int) - Current port of the Modbus server
        """
        self.ipaddr = ipaddr
        if (self.ipaddr == None): self.ipaddr = DEFAULT_IP_ADDR

        self.port = tcp_port
        if (self.port == None): self.port = DEFAULT_TCP_PORT

        # Address of generator (not IP address). Always 0x0A
        self.hdr_addr_bytes = struct.pack('>B', 0x0A)
        self.proto_id_bytes = struct.pack('>H', 0x0000) # protocol identification
        self.trans_num = 1 # transaction number used for building modbus cmd

        self.pmsg = Psi_Message()

        return

    def build_mb_cmd(self, cmd_num: int, func_code: str, data: int=None)->bytes:
        """
        Bulds the command to be sent to the Modbus server
        
        Inputs:
            cmd_num   (int)       - Command number.
            func_code (str)       - Function code. Either 'r' for a read
                                    operation or 'w' for a write operation
            data      (opt, int)  - If preforming a write operation this will be
                                    the data that is to be written
        
        Outputs:
            cmd = (bytes) - Command to be sent to the Modbus server. This will be
                            between 12 and 260 Bytes long
        """
        func_id = f'{__name__}.buid_mb_cmd'
        trans_num_bytes = struct.pack('>H', self.trans_num)
        cmd_num_bytes = struct.pack('>H', cmd_num) # byte representation of command number

        if (func_code == 'r'):
            hdr_bytes = struct.pack('>H', 0x0A41)
            data_bytes = struct.pack('>H', 0x0001)
        else:
            hdr_bytes = struct.pack('>H', 0x0A42)
#            data_bytes = struct.pack('>i', data)
            data_bytes = struct.pack('>I', data)

        data_len = len(hdr_bytes) + len(cmd_num_bytes) + len(data_bytes)
        data_len_bytes = struct.pack('>H', data_len)

        cmd = (trans_num_bytes +
               self.proto_id_bytes +
               data_len_bytes +
               hdr_bytes +
               cmd_num_bytes +
               data_bytes)

        self.trans_num += 1

        return cmd

    def parse_read_response(self, resp: bytes) -> bytes:
        """
        Parse the response give by the server due to a read command
        
        Inputs:
           resp (optional) - Bytes returned from the server
        
        Outputs:
           resp_data - This is a byte string representing the reponse from the
                       server.
        """
        func_id = f'{__name__}.parse_read_response'

        err_idx = 7
        msg_len_idx = 8
        msg_start_idx = 9

        # Checking for response error form server
        # If the highest bit of fcode is 1, then there was an
        # invalid command exception given to us from the server
        fcode = resp[err_idx]
        if (fcode > 127):
            err_msg = f'Invalid command error: {resp[msg_len_idx]}'
            self.pmsg.error(func_id, err_msg)
            return 

        length_data = resp[msg_len_idx]
        resp_data = struct.unpack(f'>{length_data}s', resp[msg_start_idx:])[0]

        return resp_data

    def parse_write_response(self, resp: bytes) -> bytes:
        """
        Parse the response given by the server due to a write command
        
        Inputs:
           resp (bytes) - Byte string returned from the server
        
        Outputs:
           resp_data (bytes) - Byte string representing the reponse from the
                               server.
        """
        func_id = f'{__name__}.parse_write_response'

        err_idx = 7
        cmd_num_high = 8
        cmd_num_low = 9
        msg_start_idx = 10

        # Checking for response error form server
        # If the highest bit of fcode is 1, then there was an
        # invalid command exception given to us from the server
        fcode = resp[err_idx]
        if (fcode > 127):
            err_msg = f'Invalid command error: {resp[cmd_num_high]}'
            self.pmsg.error(func_id, err_msg)
            return None

        return None

    def send_cmd(self, cmd: bytes, func_code: str) -> bytes:
        """
        Sends a byte string obtained from Modbus_Client.build_mb_cmd to the
        Modbus server.
        
        Inputs:
            cmd (bytes)     - Byte string representing the command to be passed
                              to the modbus server
            func_code (str) - Read/wrte code. If a read command then
                              func_code = 'r'. If a write command then
                              func_code = 'w'
        
        Outputs:
            resp (Bytes) - Byte string representing the response from the modbus
                           server. Returns none if there was a failure to connect
                           to the server
        """
        func_id = f'{__name__}.send_cmd'

        resp = None
        with ModbusTcpClient(self.ipaddr, port=self.port) as client:
            if (client.connect()):
                client.socket.send(cmd)
                response = client.socket.recv(1024)
                if (func_code == 'r'):
                    resp = self.parse_read_response(response)
                else:
                    resp = self.parse_write_response(response)

            else:
                err_msg = 'Cannot connect to server'
                self.pmsg.error(func_id, err_msg)
                resp = -1

        return resp
















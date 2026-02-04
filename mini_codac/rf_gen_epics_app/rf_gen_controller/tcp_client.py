
import socket
import struct
import time

def tcp_client(server_ip, port):

    CHUNK = 1024

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((server_ip, int(port)))

        for icur in range(0,10):
#            sock.sendall(b"more")
#            sock.sendall(b" VE?")
#            sock.sendall(b"*IDN?")
#            print('blah')
            if (icur == 0):
                print(f'icur: {icur}')
                sock.sendall(b"IPADDR?")
            elif (icur == 1):
                print(f'icur: {icur}')
                sock.sendall(b"IPMODE?")
            elif (icur == 2):
                print(f'icur: {icur}')
                sock.sendall(b"HOSTNAME?")
            else:
                print(f'icur: {icur}')
                sock.sendall(b"*IDN?")

            data = sock.recv(CHUNK)
            print(f'{data!r}')
#            data = sock.recv(CHUNK)
#            print(f'{data!r}')
#            print(f"{int.from_bytes(data, byteorder='big', signed=False)}")
#
#            idx = 0
#            while (idx < 61):
#                unsigned_data = struct.unpack('I', data[idx:idx+4])[0]
#                print(f"{unsigned_data}")
#                idx += 4
#            time.sleep(5.0)

    return
























# -*- coding: utf-8 -*-
"""
Created on Wed Aug 14 10:19:22 2024

@author: Kyle Engelhorn
This script creates a gui to interface with a fyra pressure controller, a Comet
RF generator and a MCC thermocouple logger.  changes will need to be made to incoporate a second RF generator.

This script could probably be simplified and cleaned up. 
"""

from __future__ import absolute_import, division, print_function
from builtins import *  # @UnusedWildImport

from mcculw import ul
from mcculw.enums import TempScale
from mcculw.device_info import DaqDeviceInfo

try:
    from console_examples_util import config_first_detected_device
except ImportError:
    from .console_examples_util import config_first_detected_device

import tkinter as tk
from tkinter import ttk, messagebox
import serial
import time
import matplotlib.pyplot as plt
import numpy as np

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import threading
from threading import Thread, Event
from datetime import datetime
import csv

import struct
from pymodbus.client import ModbusTcpClient

#pressure controller class
class PressureController:
    def __init__(self, port='COM3', baudrate=115200, timeout=1):
        self.ser = serial.Serial(port, baudrate, timeout=timeout)
        self.ser.reset_input_buffer()  # Clear the input buffer to ensure fresh data is read
        self.ser.reset_output_buffer()  # Clear the input buffer to ensure fresh data is read
        
    def send_command(self, command):
        self.ser.reset_input_buffer()
        self.ser.reset_output_buffer()
        self.ser.write(f"{command}\r\n".encode())
        response = self.ser.readline().decode().strip()
        return response

    def read(self):
        response = self.ser.readline().decode().strip()
        return response

    def get_sensor_info(self):
        return self.send_command("A?")

    def get_sensor_device(self, sensor_number):
        return self.send_command(f"A{sensor_number}?")

    def get_vacuum_reading(self, sensor_number=None):
        if sensor_number is None:
            var=self.send_command("Vac?")
            #time.sleep(1)
            return var
        else:
            var=self.send_command(f"Vac{sensor_number}?")
            #time.sleep(1)
            return var
            
    def get_p_term(self):
        return self.send_command("P?")

    def set_p_term(self, value):
        return self.send_command(f"P={value}")

    def get_i_term(self):
        return self.send_command("I?")

    def set_i_term(self, value):
        return self.send_command(f"I={value}")

    def get_d_term(self):
        return self.send_command("D?")

    def set_d_term(self, value):
        return self.send_command(f"D={value}")

    def get_control_setpoint(self):
        return self.send_command("SPB?")

    def set_control_setpoint(self, value):
        return self.send_command(f"SPB={value}")

    def get_upper_setpoint(self, control_number):
        return self.send_command(f"SP{control_number}U?")

    def set_upper_setpoint(self, control_number, value):
        return self.send_command(f"SP{control_number}U={value}")

    def get_lower_setpoint(self, control_number):
        return self.send_command(f"SP{control_number}L?")

    def set_lower_setpoint(self, control_number, value):
        return self.send_command(f"SP{control_number}L={value}")

    def get_control_device(self, control_number):
        return self.send_command(f"SPAT{control_number}?")

    def get_sccm_flow(self):
        return self.send_command("SPF?")

    def set_sccm_flow(self, value):
        return self.send_command(f"SPF={value}")

    def get_dinamo_valve_setpoint(self):
        return self.send_command("SPS?")

    def set_dinamo_valve_setpoint(self, value):
        return self.send_command(f"SPS={value}")

    def get_units(self):
        response = self.send_command("U?")
        if response == "U=0":
            return "Torr"
        elif response == "U=1":
            return "mBar"
        elif response == "U=2":
            return "kPa"
        elif response == "U=3":
            return "Pa"
        else:
            return "Unknown"

    def set_units(self, unit_code):
        return self.send_command(f"U={unit_code}")

    def get_data_rate(self):
        return self.send_command("T?")

    def set_data_rate(self, rate):
        return self.send_command(f"T={rate}")

    def get_mode(self):
        return self.send_command("M?")

    def set_mode(self, mode):
        return self.send_command(f"M={mode}")

    def close(self):
        self.ser.close()
        
#rf generator class (communicates through Modbus protocol)
class ModbusClient:
    def __init__(self, device_ip, tcp_port, address=0x0A, protocol_identifier=0x0000):
        self.device_ip = device_ip
        self.tcp_port = tcp_port
        self.address = address
        self.protocol_identifier = protocol_identifier
        self.transaction_number = 1  # Starting transaction number

    def build_modbus_command_read(self, command_number):
        # Transaction Number (High byte, Low byte)
        transaction_number_bytes = struct.pack('>H', self.transaction_number)

        # Protocol Identifier (always 0x0000)
        protocol_identifier_bytes = struct.pack('>H', self.protocol_identifier)

        # Build the command header: Address (fixed), Function Code (0x41 for read)
        address_byte = struct.pack('B', self.address)
        function_code_byte = struct.pack('B', 0x41)  # Read function code

        # Convert the command number to its 2-byte hexadecimal representation (big-endian)
        command_number_bytes = struct.pack('>H', command_number)

        # Fixed data for read commands: 0x00 and 0x01
        data_bytes = bytes([0x00, 0x01])

        # Length of the subsequent bytes (header, command number, data)
        remaining_length = len(address_byte) + len(function_code_byte) + len(command_number_bytes) + len(data_bytes)
        remaining_length_bytes = struct.pack('>H', remaining_length)

        # Construct the full command
        command = (
            transaction_number_bytes +  # Transaction Number
            protocol_identifier_bytes +  # Protocol Identifier
            remaining_length_bytes +  # Length field (subsequent bytes)
            address_byte +  # Address
            function_code_byte +  # Function Code (0x41 for read)
            command_number_bytes +  # Command Number (converted from the integer input)
            data_bytes  # Data bytes (0x00, 0x01 for read)
        )

        # Increment transaction number for next command
        self.transaction_number += 1

        return command

    def build_modbus_command_write(self, command_number, data):
        # Transaction Number (High byte, Low byte)
        transaction_number_bytes = struct.pack('>H', self.transaction_number)

        # Protocol Identifier (always 0x0000)
        protocol_identifier_bytes = struct.pack('>H', self.protocol_identifier)

        # Build the command header: Address (fixed), Function Code (0x42 for write)
        address_byte = struct.pack('B', self.address)
        function_code_byte = struct.pack('B', 0x42)  # Write function code

        # Convert the command number to its 2-byte hexadecimal representation (big-endian)
        command_number_bytes = struct.pack('>H', command_number)

        # Convert the data to 32-bit integer format (Big-Endian)
        data_bytes = struct.pack('>I', data)

        # Length of the subsequent bytes (header, command number, data)
        remaining_length = len(address_byte) + len(function_code_byte) + len(command_number_bytes) + len(data_bytes)
        remaining_length_bytes = struct.pack('>H', remaining_length)

        # Construct the full command
        command = (
            transaction_number_bytes +  # Transaction Number
            protocol_identifier_bytes +  # Protocol Identifier
            remaining_length_bytes +  # Length field (subsequent bytes)
            address_byte +  # Address
            function_code_byte +  # Function Code (0x42 for write)
            command_number_bytes +  # Command Number
            data_bytes  # Data bytes (32-bit integer for write)
        )

        # Increment transaction number for next command
        self.transaction_number += 1

        return command

    def parse_read_response(self, response, response_type):
        if len(response) < 9:
            return "Invalid or incomplete response."

        transaction_number = struct.unpack('>H', response[0:2])[0]
        protocol_identifier = struct.unpack('>H', response[2:4])[0]
        length = struct.unpack('>H', response[4:6])[0]
        address = response[6]
        function_code = response[7]
        
        if function_code & 0x80:  # Exception code flag (high bit is set)
            exception_code = function_code
            print(f"Modbus Exception: Invalid function code or unknown parameter (Exception Code: {exception_code})")
            return

        data_length = response[8]
        data = response[9:9+data_length]

        if response_type == 'string':
            try:
                result_string = data.decode('utf-8').replace('\x00', '').strip()
            except UnicodeDecodeError:
                print(f"Failed to decode response data as string. Raw data: {data.hex()}")
                return
            return result_string

        elif response_type == 'integer':
            if len(data) == 4:
                decoded_value = struct.unpack('>I', data)[0]
                return decoded_value
            else:
                print(f"Data length is not 4 bytes. Raw data: {data.hex()}")

    def parse_write_response(self, response):
        if len(response) < 9:
            return "Invalid or incomplete response."

        transaction_number = struct.unpack('>H', response[0:2])[0]
        protocol_identifier = struct.unpack('>H', response[2:4])[0]
        length = struct.unpack('>H', response[4:6])[0]
        address = response[6]
        function_code = response[7]
        print(response)

        # Check for Modbus exception (if high bit is set in the function code)
        if function_code & 0x80:
            exception_code = function_code
            print(f"Modbus Exception: Invalid function code or unknown parameter (Exception Code: {exception_code})")
            return

        # Command number comes from bytes 8-9 in the response
        command_number = struct.unpack('>H', response[8:10])[0]

        # Data is typically 4 bytes for write responses (32-bit integer)
        data = response[10:]

        if len(data) == 4:
            decoded_value = struct.unpack('>I', data)[0]
            return decoded_value
        else:
            print(f"Data length is not 4 bytes. Raw data: {data.hex()}")

    def send_modbus_read_command(self, command_number, response_type='string'):
        command = self.build_modbus_command_read(command_number)

        # Create a Modbus TCP client
        client = ModbusTcpClient(self.device_ip, port=self.tcp_port)

        if client.connect():
            client.socket.send(command)
            response = client.socket.recv(1024)
            data = self.parse_read_response(response, response_type)
            client.close()
            return data
        else:
            print("Failed to connect to the device")

    def send_modbus_write_command(self, command_number, data):
        command = self.build_modbus_command_write(command_number, data)

        # Create a Modbus TCP client
        client = ModbusTcpClient(self.device_ip, port=self.tcp_port)

        if client.connect():
            client.socket.send(command)
            response = client.socket.recv(1024)
            data = self.parse_write_response(response)
            client.close()
            return data
        else:
            print("Failed to connect to the device")

#mappings for rf generator read state command
def map_state(state_value):
    """Map the integer state to its corresponding state description and color."""
    states = {
        0: ("Not Ready", "gray"),
        1: ("Ready (RF Off)", "green"),
        2: ("Active (RF On)", "red"),
        3: ("Error (RF Off)", "yellow")
    }
    return states.get(state_value, ("Unknown State", "gray"))

#mapping of matching modes
def map_matching_mode(mode_value):
    """Map the matching mode integer to the mode description."""
    modes = {
        1: "Manual",
        2: "Auto"
    }
    return modes.get(mode_value, "Unknown")
            
            
#the GUI, consider renaming GUI function...   
class PressureControllerApp:
    def __init__(self, root):
        #define gui items
        self.root = root
        self.root.title("Plasma Controller GUI")
        
        #define control objects and read threads
        self.fyra = None
        self.comet = None
        
        self.running = None
        self.data_listener_thread = None
        self.display_pressure_thread = None
        
        
        #pressure controller variables
        self.fyra_port = tk.StringVar()
        self.fyra_press_set_new = tk.StringVar()
        self.fyra_press_set_curr = tk.StringVar()
        self.fyra_command_man = tk.StringVar()
        self.fyra_command_response = tk.StringVar()
        self.fyra_press_unit = tk.StringVar()
        self.fyra_press_1 = tk.StringVar()
        self.fyra_press_2 = tk.StringVar()
        
        #thermocouple variables
        self.mcc_board_num = 0
        ####belwo not necessary?
        #self.mcc_tc_1 = tk.StringVar()
        #self.mcc_tc_2 = tk.StringVar()
        #self.mcc_tc_3 = tk.StringVar()
        #self.mcc_tc_4 = tk.StringVar()
        
        #rf generator1 variables
        self.comet1_state = tk.StringVar()
        self.comet1_power_set_curr = tk.DoubleVar()
        self.comet1_power_set_new = tk.DoubleVar()
        self.comet1_power_fwd = tk.DoubleVar()
        self.comet1_power_ref = tk.DoubleVar()
        self.comet1_cap_tune = tk.DoubleVar()
        self.comet1_cap_load = tk.DoubleVar()
        self.comet1_cap_tune_set = tk.DoubleVar()
        self.comet1_cap_load_set = tk.DoubleVar()
        self.comet1_command_number = tk.StringVar()
        self.comet1_command_type = tk.StringVar()
        self.comet1_command_data = tk.StringVar()
        self.comet1_command_response = tk.StringVar()
        #self.comet1_phase_set = tk.DoubleVar()

        #rf generator2 variables
        self.comet2_state = tk.StringVar()
        self.comet2_power_set_curr = tk.DoubleVar()
        self.comet2_power_set_new = tk.DoubleVar()
        self.comet2_power_fwd = tk.DoubleVar()
        self.comet2_power_ref = tk.DoubleVar()
        self.comet2_cap_tune = tk.DoubleVar()
        self.comet2_cap_load = tk.DoubleVar()
        self.comet2_cap_tune_set = tk.DoubleVar()
        self.comet2_cap_load_set = tk.DoubleVar()
        self.comet2_command_number = tk.StringVar()
        self.comet2_command_type = tk.StringVar()
        self.comet2_command_data = tk.StringVar()
        self.comet2_command_response = tk.StringVar()
        self.comet2_phase_set = tk.DoubleVar()
        self.comet2_phase = tk.DoubleVar()
        
        self.create_widgets()
        
        #data and some flags
        self.data = pd.DataFrame(columns=['Timestamp', 'Minutes', 'Sensor1', 'Sensor2', 'Units','TC1','TC2','TC3','TC4',"Forward_Power1","Reflected_Power1", "Load_Pos1", "Tune_Pos1","Forward_Power2","Reflected_Power2", "Load_Pos2", "Tune_Pos2","Phase2"])
        self.record = False
        self.disable=False
        self.log_plot=False
        self.start_time = None

    def create_widgets(self):
        #setup frame
        frame = ttk.Frame(self.root, padding=10)
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        #COM Port, Connect
        ttk.Label(frame, text="COM Port:").grid(row=0, column=0, sticky=tk.W)
        port_entry = ttk.Entry(frame, textvariable=self.fyra_port)
        port_entry.grid(row=0, column=1, sticky=(tk.W, tk.E))
        ttk.Button(frame, text="Connect", command=self.connect).grid(row=0, column=2,sticky=tk.W)
        
        #Manual Command and Send
        ttk.Label(frame, text="Man. Comm.:").grid(row=0, column=3, sticky=tk.W)
        manual_entry = ttk.Entry(frame, textvariable=self.fyra_command_man)
        manual_entry.grid(row=0, column=4, sticky=(tk.W, tk.E))
        ttk.Button(frame, text="Send", command=self.send_manual_command).grid(row=0, column=5,sticky=tk.W)
        
        #Command Response
        ttk.Label(frame, text="Resp.:").grid(row=1, column=3, sticky=tk.W)
        ttk.Label(frame, textvariable=self.fyra_command_response).grid(row=1, column=4, sticky=(tk.W, tk.E))
        
        #Sensor 1, Disable All, #Sensor2
        ttk.Label(frame, text="Sensor 1:").grid(row=1, column=0, sticky=tk.W)
        ttk.Label(frame, textvariable=self.fyra_press_1).grid(row=1, column=1, sticky=(tk.W, tk.E))
        ttk.Button(frame, text="Disable All", command=self.disable).grid(row=1, column=2,sticky=tk.W) 
        ttk.Label(frame, text="Sensor 2:").grid(row=2, column=0, sticky=tk.W)
        ttk.Label(frame, textvariable=self.fyra_press_2).grid(row=2, column=1, sticky=(tk.W, tk.E))
        
        #current setpoint, set, Disable
        ttk.Label(frame, text="Current Setpoint:").grid(row=3, column=0, sticky=tk.W)
        ttk.Label(frame, textvariable=self.fyra_press_set_curr).grid(row=3, column=1, sticky=(tk.W, tk.E))
        ttk.Label(frame, text="Control Setpoint:").grid(row=4, column=0, sticky=tk.W)
        setpoint_entry = ttk.Entry(frame, textvariable=self.fyra_press_set_new)
        setpoint_entry.grid(row=4, column=1, sticky=(tk.W, tk.E))
        ttk.Button(frame, text="Set", command=self.set_control_setpoint).grid(row=4, column=2,sticky=tk.W)
        ttk.Button(frame, text="Disable Press. Cont.", command=self.disable_control).grid(row=4, column=3)
        
        #record light, Start, Stop, Clear data
        self.recording_light = tk.Canvas(frame, width=20, height=20, bg="grey")  # Default color is grey (off)
        self.recording_light.grid(row=5, column=0)
        ttk.Button(frame, text="Start Recording", command=self.start_recording).grid(row=5, column=1,sticky=tk.W)
        ttk.Button(frame, text="Stop Recording", command=self.stop_recording).grid(row=5, column=2,sticky=tk.W)
        ttk.Button(frame, text="Clear Data", command=self.clear_data).grid(row=5, column=3,sticky=tk.W)


        #Xmin, Xmax, Y1Min, Y1Max, Y2Min, Y2Max
        ttk.Label(frame, text="X-axis Min:").grid(row=6, column=0,sticky=tk.W)
        self.x_min_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.x_min_var).grid(row=6, column=1)
        ttk.Label(frame, text="X-axis Max:").grid(row=7, column=0,sticky=tk.W)
        self.x_max_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.x_max_var).grid(row=7, column=1)
        ttk.Label(frame, text="Y1-axis Min (Sensor 1):").grid(row=6, column=2,sticky=tk.W)
        self.y1_min_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.y1_min_var).grid(row=6, column=3)
        ttk.Label(frame, text="Y1-axis Max (Sensor 1):").grid(row=7, column=2,sticky=tk.W)
        self.y1_max_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.y1_max_var).grid(row=7, column=3)
        ttk.Label(frame, text="Y2-axis Min (Sensor 2):").grid(row=6, column=4,sticky=tk.W)
        self.y2_min_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.y2_min_var).grid(row=6, column=5)
        ttk.Label(frame, text="Y2-axis Max (Sensor 2):").grid(row=7, column=4,sticky=tk.W)
        self.y2_max_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.y2_max_var).grid(row=7, column=5)
        #Linear, Log
        ttk.Button(frame, text="Linear", command=self.plot_linear).grid(row=8, column=0,sticky=tk.W)
        ttk.Button(frame, text="Log", command=self.plot_log).grid(row=8, column=1,sticky=tk.W)            
        
        
        # IP address, state light, Start, Stop, Clear
        ttk.Label(frame, text="Generator 1").grid(row=0, column=6,sticky=tk.W)
        self.state_light1 = tk.Canvas(frame, width=20, height=20, bg="grey")  # Default color is grey (off/Not ready)
        self.state_light1.grid(row=0, column=8)
        ttk.Label(frame, text="State:").grid(row=0, column=9, sticky=tk.W)
        ttk.Label(frame, textvariable=self.comet1_state).grid(row=0, column=10, sticky=(tk.W, tk.E))
        
        #RF On, RF OFF, Mode Light, Manual and Auto Matching
        ttk.Button(frame, text="RF ON!", command=self.rf_on1).grid(row=1, column=6,sticky=tk.W)
        ttk.Button(frame, text="RF OFF!", command=self.rf_off1).grid(row=1, column=7,sticky=tk.W)
        
        self.matching_light1 = tk.Canvas(frame, width=20, height=20, bg="grey")  # Default color is grey (off/Not ready)
        self.matching_light1.grid(row=1, column=8)
        ttk.Button(frame, text="Auto Match", command=self.auto_match1).grid(row=1, column=9,sticky=tk.W)
        ttk.Button(frame, text="Man. Match", command=self.manual_match1).grid(row=1, column=10,sticky=tk.W)

        #Power Setpoint, Set RF Power
        ttk.Label(frame, text="Pwr Set:").grid(row=2, column=6, sticky=tk.W)
        ttk.Label(frame, textvariable=self.comet1_power_set_curr).grid(row=2, column=7, sticky=(tk.W, tk.E))
        ttk.Label(frame, text="Set Pwr:").grid(row=2, column=8, sticky=tk.W)
        power_entry1 = ttk.Entry(frame, textvariable=self.comet1_power_set_new)
        power_entry1.grid(row=2, column=9, sticky=(tk.W, tk.E))
        ttk.Button(frame, text="Set", command=self.set_power1).grid(row=2, column=10,stick=tk.W)
        
        #Forward Power
        ttk.Label(frame, text="Fwd Pwr:").grid(row=3, column=6, sticky=tk.W)
        ttk.Label(frame, textvariable=self.comet1_power_fwd).grid(row=3, column=7, sticky=(tk.W, tk.E))
      
        #Reflected Power
        ttk.Label(frame, text="Ref. Pwr:").grid(row=4, column=6, sticky=tk.W)
        ttk.Label(frame, textvariable=self.comet1_power_ref).grid(row=4, column=7, sticky=(tk.W, tk.E))
        
        #Load Capacitor, Set Load Capacitor        
        ttk.Label(frame, text="Load Cap.:").grid(row=5, column=6, sticky=tk.W)
        ttk.Label(frame, textvariable=self.comet1_cap_load).grid(row=5, column=7, sticky=(tk.W, tk.E))
        ttk.Label(frame, text="Set Load Cap.:").grid(row=5, column=8, sticky=tk.W)
        load_entry1 = ttk.Entry(frame, textvariable=self.comet1_cap_load_set)
        load_entry1.grid(row=5, column=9, sticky=(tk.W, tk.E))
        ttk.Button(frame, text="Set", command=self.set_load_cap1).grid(row=5, column=10,stick=tk.W)
    
        
        #Tune Capacitor, Set Tune Capacitor
        ttk.Label(frame, text="Tune Cap.:").grid(row=6, column=6, sticky=tk.W)
        ttk.Label(frame, textvariable=self.comet1_cap_tune).grid(row=6, column=7, sticky=(tk.W, tk.E))
        ttk.Label(frame, text="Set Tune Cap.:").grid(row=6, column=8, sticky=tk.W)
        tune_entry1 = ttk.Entry(frame, textvariable=self.comet1_cap_tune_set)
        tune_entry1.grid(row=6, column=9, sticky=(tk.W, tk.E))
        ttk.Button(frame, text="Set", command=self.set_tune_cap1).grid(row=6, column=10,stick=tk.W)


        
        #Manual Command, Data type, Read and Write
        ttk.Label(frame, text="Comm. #:").grid(row=7, column=6, sticky=tk.W)
        command_entry1 = ttk.Entry(frame, textvariable=self.comet1_command_number)
        command_entry1.grid(row=7, column=7, sticky=(tk.W, tk.E))
        ttk.Label(frame, text="Dtype:").grid(row=7, column=8, sticky=tk.W)
        type_entry1 = ttk.Entry(frame, textvariable=self.comet1_command_type)
        type_entry1.grid(row=7, column=9, sticky=(tk.W, tk.E))
        ttk.Button(frame, text="Read", command=self.rf_read1).grid(row=7, column=10,sticky=tk.W)
        ttk.Label(frame, text="Data:").grid(row=8, column=6, sticky=tk.W)
        data_entry1 = ttk.Entry(frame, textvariable=self.comet1_command_data)
        data_entry1.grid(row=8, column=7, sticky=(tk.W, tk.E))
        ttk.Button(frame, text="Write", command=self.rf_write1).grid(row=8, column=8,sticky=tk.W)
        
        #read/write response Data
        ttk.Label(frame, text="Resp.:").grid(row=8, column=9, sticky=tk.W)
        ttk.Label(frame, textvariable=self.comet1_command_response).grid(row=8, column=10, sticky=tk.W)

########
        ttk.Label(frame, text="Generator 2").grid(row=0, column=12,sticky=tk.W)
        self.state_light2 = tk.Canvas(frame, width=20, height=20, bg="grey")  # Default color is grey (off/Not ready)
        self.state_light2.grid(row=0, column=14)
        ttk.Label(frame, text="State:").grid(row=0, column=15, sticky=tk.W)
        ttk.Label(frame, textvariable=self.comet2_state).grid(row=0, column=16, sticky=(tk.W, tk.E))
        
        #RF On, RF OFF, Mode Light, Manual and Auto Matching
        ttk.Button(frame, text="RF ON!", command=self.rf_on2).grid(row=1, column=12,sticky=tk.W)
        ttk.Button(frame, text="RF OFF!", command=self.rf_off2).grid(row=1, column=13,sticky=tk.W)
        
        self.matching_light2 = tk.Canvas(frame, width=20, height=20, bg="grey")  # Default color is grey (off/Not ready)
        self.matching_light2.grid(row=1, column=14)
        ttk.Button(frame, text="Auto Match", command=self.auto_match2).grid(row=1, column=15,sticky=tk.W)
        ttk.Button(frame, text="Man. Match", command=self.manual_match2).grid(row=1, column=16,sticky=tk.W)

        #Power Setpoint, Set RF Power
        ttk.Label(frame, text="Pwr Set:").grid(row=2, column=12, sticky=tk.W)
        ttk.Label(frame, textvariable=self.comet2_power_set_curr).grid(row=2, column=13, sticky=(tk.W, tk.E))
        ttk.Label(frame, text="Set Pwr:").grid(row=2, column=14, sticky=tk.W)
        power_entry2 = ttk.Entry(frame, textvariable=self.comet2_power_set_new)
        power_entry2.grid(row=2, column=15, sticky=(tk.W, tk.E))
        ttk.Button(frame, text="Set", command=self.set_power2).grid(row=2, column=16,stick=tk.W)
        
        #Forward Power
        ttk.Label(frame, text="Fwd Pwr:").grid(row=3, column=12, sticky=tk.W)
        ttk.Label(frame, textvariable=self.comet2_power_fwd).grid(row=3, column=13, sticky=(tk.W, tk.E))
      
        #Reflected Power
        ttk.Label(frame, text="Ref. Pwr:").grid(row=4, column=12, sticky=tk.W)
        ttk.Label(frame, textvariable=self.comet2_power_ref).grid(row=4, column=13, sticky=(tk.W, tk.E))
        
        #Load Capacitor, Set Load Capacitor        
        ttk.Label(frame, text="Load Cap.:").grid(row=5, column=12, sticky=tk.W)
        ttk.Label(frame, textvariable=self.comet2_cap_load).grid(row=5, column=13, sticky=(tk.W, tk.E))
        ttk.Label(frame, text="Set Load Cap.:").grid(row=5, column=14, sticky=tk.W)
        load_entry2 = ttk.Entry(frame, textvariable=self.comet2_cap_load_set)
        load_entry2.grid(row=5, column=15, sticky=(tk.W, tk.E))
        ttk.Button(frame, text="Set", command=self.set_load_cap2).grid(row=5, column=16,stick=tk.W)
    
        
        #Tune Capacitor, Set Tune Capacitor
        ttk.Label(frame, text="Tune Cap.:").grid(row=6, column=12, sticky=tk.W)
        ttk.Label(frame, textvariable=self.comet2_cap_tune).grid(row=6, column=13, sticky=(tk.W, tk.E))
        ttk.Label(frame, text="Set Tune Cap.:").grid(row=6, column=14, sticky=tk.W)
        tune_entry2 = ttk.Entry(frame, textvariable=self.comet2_cap_tune_set)
        tune_entry2.grid(row=6, column=15, sticky=(tk.W, tk.E))
        ttk.Button(frame, text="Set", command=self.set_tune_cap2).grid(row=6, column=16,stick=tk.W)

        
        #Manual Command, Data type, Read and Write
        ttk.Label(frame, text="Comm. #:").grid(row=7, column=12, sticky=tk.W)
        command_entry2 = ttk.Entry(frame, textvariable=self.comet2_command_number)
        command_entry2.grid(row=7, column=13, sticky=(tk.W, tk.E))
        ttk.Label(frame, text="Dtype:").grid(row=7, column=14, sticky=tk.W)
        type_entry2 = ttk.Entry(frame, textvariable=self.comet2_command_type)
        type_entry2.grid(row=7, column=15, sticky=(tk.W, tk.E))
        ttk.Button(frame, text="Read", command=self.rf_read2).grid(row=7, column=16,sticky=tk.W)
        ttk.Label(frame, text="Data:").grid(row=8, column=12, sticky=tk.W)
        data_entry2 = ttk.Entry(frame, textvariable=self.comet2_command_data)
        data_entry2.grid(row=8, column=13, sticky=(tk.W, tk.E))
        ttk.Button(frame, text="Write", command=self.rf_write2).grid(row=8, column=14,sticky=tk.W)
        
        #read/write response Data
        ttk.Label(frame, text="Resp.:").grid(row=8, column=15, sticky=tk.W)
        ttk.Label(frame, textvariable=self.comet2_command_response).grid(row=8, column=16, sticky=tk.W)        
        
        #Phase

        ttk.Label(frame, text="Phase:").grid(row=3, column=14, sticky=tk.W)
        ttk.Label(frame, textvariable=self.comet2_phase).grid(row=3, column=15, sticky=(tk.W, tk.E))
        ttk.Label(frame, text="Set Phase:").grid(row=4, column=14, sticky=tk.W)
        phase_entry2 = ttk.Entry(frame, textvariable=self.comet2_phase_set)
        phase_entry2.grid(row=4, column=15, sticky=(tk.W, tk.E))
        ttk.Button(frame, text="Set", command=self.set_phase2).grid(row=4, column=16,stick=tk.W)

        
        #figure, 2x2 with ax_press_1/2 for pressure, ax_tc for temp, ax_power_fwd/4 for power and ax_cap for capacitors
        #consider simplifying naming
        
        #pressure plots
        plt.rcParams.update({'font.size': 8})
        self.figure = plt.figure(figsize=(12,6))
        gs = self.figure.add_gridspec(2,2, hspace=0,wspace=.35,left=.08,right=.92,bottom=.08, top=.92)
        self.ax = gs.subplots(sharex=True)
        #self.figure, self.ax = plt.subplots(nrows=2,ncols=2,figsize=(12,6),sharex=True)
        
        
        self.ax_press_1=self.ax[0,0]
        self.ax_press_2 = self.ax_press_1.twinx()
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.root)
        self.canvas.get_tk_widget().grid(row=9, column=0,columnspan=13,sticky=tk.W)
        self.line_press_1, = self.ax_press_1.plot([], [], 'b-', label='Sensor 1')
        self.line_press_2, = self.ax_press_2.plot([], [], 'r-', label='Sensor 2')
        self.ax_press_1.set_xlabel('Time (minutes)')
        self.ax_press_1.set_ylabel('Sensor 1', color='b')
        self.ax_press_2.set_ylabel('Sensor 2', color='r')
        self.ax_press_1.legend(loc='upper left')
        self.ax_press_2.legend(loc='upper right')
        
        #Temperature plots
        self.ax_tc=self.ax[1,0]
        self.line_tc_1, = self.ax_tc.plot([], [], 'b-', label='TC 1')
        self.line_tc_2, = self.ax_tc.plot([], [], 'r-', label='TC 2')
        self.line_tc_3, = self.ax_tc.plot([], [], 'g-', label='TC 3')
        self.lineTC4, = self.ax_tc.plot([], [], 'm-', label='TC 4')        
        self.ax_tc.set_xlabel('Time (minutes)')
        self.ax_tc.set_ylabel('Temp [C]', color='b')
        self.ax_tc.legend(loc='upper left')

        #Power plots
        self.ax_power_fwd=self.ax[0,1]
        self.ax_power_ref = self.ax_power_fwd.twinx()
        self.line_power_fwd1, = self.ax_power_fwd.plot([], [], 'b-', label='Forward Power 1')
        self.line_power_ref1, = self.ax_power_ref.plot([], [], 'r-', label='Reflected Power 1')
        self.line_power_fwd2, = self.ax_power_fwd.plot([], [], 'b--', label='Forward Power 2')
        self.line_power_ref2, = self.ax_power_ref.plot([], [], 'r--', label='Reflected Power 2')      
        self.ax_power_fwd.set_xlabel('Time [minutes]')
        self.ax_power_fwd.set_ylabel('Forward Power [W]', color='b')
        self.ax_power_ref.set_ylabel('Reflected Power [W]', color='r')
        #self.ax_power_fwd.legend(loc='upper left')
        #self.ax_power_ref.legend(loc='upper right')
        
        #Capacitor Plots
        self.ax_cap=self.ax[1,1]
        self.line_cap_tune1, = self.ax_cap.plot([], [], 'b-', label='Load Cap. 1')
        self.line_cap_load1, = self.ax_cap.plot([], [], 'r-', label='Tune Cap. 1')
        self.line_cap_tune2, = self.ax_cap.plot([], [], 'b--', label='Load Cap. 2')
        self.line_cap_load2, = self.ax_cap.plot([], [], 'r--', label='Tune Cap. 2')  
        self.ax_cap.set_xlabel('Time [minutes]')
        self.ax_cap.set_ylabel('Position %', color='b')
        self.ax_cap.legend(loc='upper left')
    
    #connect all the HW   
    def connect(self):
        
        #connect TC controller
        use_device_detection = True
        dev_id_list = []

        try:
            if use_device_detection:
                config_first_detected_device(self.mcc_board_num, dev_id_list)

            daq_dev_info = DaqDeviceInfo(self.mcc_board_num)

            print('\nActive DAQ device: ', daq_dev_info.product_name, ' (',
                  daq_dev_info.unique_id, ')\n', sep='')

            ai_info = daq_dev_info.get_ai_info()
            if ai_info.num_temp_chans <= 0:
                raise Exception('Error: The DAQ device does not support '
                                'temperature input')
        except Exception as e:
            print('\n', e)

############################################        
    #connect rf gnerator1
        try:
            
            #use default port if not specified
            self.comet1 = ModbusClient(device_ip="169.254.1.1", tcp_port=502)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to connect: {e}") 
    #connect rf gnerator2
        try:
            
            #use default port if not specified
            self.comet2 = ModbusClient(device_ip="169.254.1.2", tcp_port=502)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to connect: {e}")        
        
        #connect pressure controller and start threads
        try:
            port = self.fyra_port.get()
            
            #use default port if not specified 
            if port == '': 
                self.fyra = PressureController()
            else:
                self.fyra = PressureController(port)
            
            time.sleep(2) #allow time for connection to establish
            
            #loops to make sure the command is sent and received
            response='Unknown'
            while response == 'Unknown': 
                response=self.fyra.get_units()
                #print(response)
            self.fyra_press_unit.set(response)
            
            while response != 'M=A': 
                response=self.fyra.set_mode('A')
                #print(response)
                
            #self.running = True
            #######################
            self.running= Event()
            self.running.set()
            self.suspended=Event()

            ##############
            self.data_listener_thread = Thread(target=self.read_continuous_data, daemon=True)
            self.data_listener_thread.start()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to connect: {e}")
            

    #send the control setpoint to the controller which also turns on the pressure control.
    def set_control_setpoint(self):
        try:
            self.suspended.set()
            response='Unknown'
            while response != 'M=M': 
                response=self.fyra.set_mode('M')
            
            setpoint = self.fyra_press_set_new.get()
            response = self.fyra.set_control_setpoint(setpoint)
            
            response='Unknown'
            while response != 'M=A': 
                response=self.fyra.set_mode('A')
            
            self.suspended.clear()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to set control setpoint: {e}")
    
    #disable pressure control by switching to flow control mode and setting flow to 0         
    def disable_control(self):
        try:
            self.suspended.set()
            response='Unknown'
            while response != 'M=M': 
                response=self.fyra.set_mode('M')
                
            response = self.fyra.set_sccm_flow(0)
            response='Unknown'
            while response != 'M=A': 
                response=self.fyra.set_mode('A')
            
            self.suspended.clear()         
        except Exception as e:
            messagebox.showerror("Error", f"Failed to disable control: {e}")
   
    #disable the threads and close all the threads. 
    def disable(self):
        if self.fyra is not None:
            self.disable_control()
            self.fyra.close()
        if self.data_listener_thread is not None:
            self.data_listener_thread.join()
        if self.running is not None:    
            self.running.clear()
        self.disable = True

    #simple variable to set log plot off
    def plot_linear(self):
        self.log_plot = False
    
    #simple variable to set log plot on
    def plot_log(self):
        self.log_plot = True
    
    #send and record manual command to pressure controller
    ########should clean up command names
    def send_manual_command(self):
        try:
            self.suspended.set()
            response='Unknown'
            while response != 'M=M': 
                response=self.fyra.set_mode('M')
                
            command = self.fyra_command_man.get()
            
            while response =='M=M':
                response = self.fyra.send_command(command)
                self.fyra_command_response.set(f"{response}")
            
            while response != 'M=A': 
                response=self.fyra.set_mode('A')
            
            self.suspended.clear()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send command: {e}")


    #simple variable to enable data saving    
    def start_recording(self):
        self.record = True
        self.recording_light.config(bg="red")
        
    #simple variable to stop data saving
    def stop_recording(self):
        self.record = False
        self.recording_light.config(bg="grey")
        
    def clear_data(self):
        self.data = pd.DataFrame(columns=['Timestamp', 'Minutes', 'Sensor1', 'Sensor2', 'Units','TC1','TC2','TC3','TC4',"Forward_Power1","Reflected_Power1", "Load_Pos1", "Tune_Pos1","Forward_Power2","Reflected_Power2", "Load_Pos2", "Tune_Pos2","Phase2"])
        self.start_time = datetime.now()
    
    #read, parse, update plot and save
    #this function reads the data from the pressure controller and passes it to parse and update,
    #but perhaps this should be broken up as parse and update is very long and complicated
    #need to add error/data handling when one or both of the gauges are not reading
    def read_continuous_data(self):
        if self.start_time is None:
           self.start_time = datetime.now()
           
        while self.running.is_set():
            if self.suspended.is_set():
                time.sleep(.5)
                continue
            
            line = self.fyra.ser.readline().decode().strip()
            if line:
                self.parse_and_update(line)
                self.update_plot
                
    #parses the lines from the conroller format is either:
    #VAC1=1.00e+01 VAC2=2.02e+01 SPB=9.9990 P=10.0000 I=0.0100 D=5.0000 O=99
    #if pressure control is enabled to a value of 10 or
    #VAC1=9.88e+00 VAC2=2.01e+01 SPF=0
    #if pressure control is disabled and flow is set to 0
    
    def parse_and_update(self, line):
        try:
            # Parsing Logic
            parts = line.split()
            data = {}
            for part in parts:
                key, value = part.split('=')
                data[key] = value

            #get the values from the 2 pressure sensors and the setpoint
            pressure_1=data.get('VAC1', 0)
            pressure_2=data.get('VAC2', 0)
            self.fyra_press_1.set(f"{data.get('VAC1', 0)} {self.fyra_press_unit.get()}")
            self.fyra_press_2.set(f"{data.get('VAC2', 0)} {self.fyra_press_unit.get()}")
            self.fyra_press_set_curr.set(f"{data.get('SPF', data.get('SPB', 0))}")
            
            if pressure_1=='RANGE':
                pressure_1=-1
            else:
                pressure_1=float(pressure_1)
            
            if pressure_2=='RANGE':
                pressure_2=-1
            else:
                pressure_2=float(pressure_2)
                
            #read the thermocouple data
            TC1 = ul.t_in(self.mcc_board_num, 0, TempScale.CELSIUS)
            TC2 = ul.t_in(self.mcc_board_num, 1, TempScale.CELSIUS)
            TC3 = ul.t_in(self.mcc_board_num, 2, TempScale.CELSIUS)
            TC4 = ul.t_in(self.mcc_board_num, 3, TempScale.CELSIUS)
            
            #get all the rf generator data
           
            # Read the state (command 8000)
            state_value1 = self.comet1.send_modbus_read_command(command_number=8000, response_type='integer')
            if state_value1 is not None:
                state_description1, color = map_state(state_value1)
                self.comet1_state.set(state_description1)
                self.state_light1.config(bg=color)
            else:
                self.comet1_state.set( "Failed to read state")
                self.state_light1.config(bg="grey")
            
            # Read the matching mode (command 8201)
            match_value = self.comet1.send_modbus_read_command(command_number=8201, response_type='integer')
            if match_value is not None:
                if match_value==2:
                    self.matching_light1.config(bg="green")
                if match_value==1:
                    self.matching_light1.config(bg="red")
            else:
                self.matching_light1.config(bg="grey")
                
            # Read the RF Setpoint (command 1206) and convert to W
            setpoint_value = self.comet1.send_modbus_read_command(command_number=1206, response_type='integer')
            if setpoint_value is not None:
                setpoint_w = setpoint_value / 1000.0  # Convert from mW to W
                self.comet1_power_set_curr.set(setpoint_w)
            else:
                self.comet1_power_set_curr.set(-1)           
            
            # Read the Forward Power (command 8021) and convert to W
            forward_power_value = self.comet1.send_modbus_read_command(command_number=8021, response_type='integer')
            if forward_power_value is not None:
                forward_power_w = forward_power_value / 1000.0  # Convert from mW to W
                self.comet1_power_fwd.set(forward_power_w)
            else:
                self.comet1_power_fwd.set(-1) 
            '''
            # Read the Forward Power (command 1112) and convert to W
            phase_value = self.comet1.send_modbus_read_command(command_number=1112, response_type='integer')
            if forward_power_value is not None:
                self.comet1_phase.set(phase_value)
            else:
                self.comet1_power_fwd.set(-1)                 
            '''
            # Read the Reflected Power (command 8022) and convert to W
            reflected_power_value = self.comet1.send_modbus_read_command(command_number=8022, response_type='integer')
            if reflected_power_value is not None:
                reflected_power_w = reflected_power_value / 1000.0  # Convert from mW to W
                self.comet1_power_ref.set(reflected_power_w) 
            else:
                self.comet1_power_ref.set(-1)
                
            # Read the Tune Capacitor Position (command 9203)
            tune_cap_position = self.comet1.send_modbus_read_command(command_number=9204, response_type='integer')
            if tune_cap_position is not None:
                self.comet1_cap_tune.set(tune_cap_position/10.0)
            else:
                self.comet1_cap_tune.set(-1)
    
            # Read the Load Capacitor Position (command 9204)
            load_cap_position = self.comet1.send_modbus_read_command(command_number=9203, response_type='integer')
            if load_cap_position is not None:
                self.comet1_cap_load.set(load_cap_position/10.0)
            else:
                self.comet1_cap_load.set(-1)
            
            #gen2
            # Read the state (command 8000)
            state_value2 = self.comet2.send_modbus_read_command(command_number=8000, response_type='integer')
            if state_value2 is not None:
                state_description, color = map_state(state_value2)
                self.comet2_state.set(state_description)
                self.state_light2.config(bg=color)
            else:
                self.comet2_state.set( "Failed to read state")
                self.state_light2.config(bg="grey")
            
            # Read the matching mode (command 8201)
            match_value = self.comet2.send_modbus_read_command(command_number=8201, response_type='integer')
            if match_value is not None:
                if match_value==2:
                    self.matching_light2.config(bg="green")
                if match_value==1:
                    self.matching_light2.config(bg="red")
            else:
                self.matching_light2.config(bg="grey")
                
            # Read the RF Setpoint (command 1206) and convert to W
            setpoint_value = self.comet2.send_modbus_read_command(command_number=1206, response_type='integer')
            if setpoint_value is not None:
                setpoint_w = setpoint_value / 1000.0  # Convert from mW to W
                self.comet2_power_set_curr.set(setpoint_w)
            else:
                self.comet2_power_set_curr.set(-1)           
            
            # Read the Forward Power (command 8021) and convert to W
            forward_power_value = self.comet2.send_modbus_read_command(command_number=8021, response_type='integer')
            if forward_power_value is not None:
                forward_power_w = forward_power_value / 1000.0  # Convert from mW to W
                self.comet2_power_fwd.set(forward_power_w)
            else:
                self.comet2_power_fwd.set(-1) 

            # Read the Forward Power (command 1112) and convert to W
            phase_value = self.comet2.send_modbus_read_command(command_number=1112, response_type='integer')
            if forward_power_value is not None:
                self.comet2_phase.set(phase_value)
            else:
                self.comet2_power_ref.set(-1)
                
            # Read the Reflected Power (command 8022) and convert to W
            reflected_power_value = self.comet2.send_modbus_read_command(command_number=8022, response_type='integer')
            if reflected_power_value is not None:
                reflected_power_w = reflected_power_value / 1000.0  # Convert from mW to W
                self.comet2_power_ref.set(reflected_power_w) 
            else:
                self.comet2_power_ref.set(-1)
                
            # Read the Tune Capacitor Position (command 9203)
            tune_cap_position = self.comet2.send_modbus_read_command(command_number=9204, response_type='integer')
            if tune_cap_position is not None:
                self.comet2_cap_tune.set(tune_cap_position/10.0)
            else:
                self.comet2_cap_tune.set(-1)
    
            # Read the Load Capacitor Position (command 9204)
            load_cap_position = self.comet2.send_modbus_read_command(command_number=9203, response_type='integer')
            if load_cap_position is not None:
                self.comet2_cap_load.set(load_cap_position/10.0)
            else:
                self.comet2_cap_load.set(-1)
                

            #get the current timme and minutes since starting data
            timestamp=datetime.now()
            minutes = (datetime.now() - self.start_time).total_seconds() / 60  # Convert to minutes
            
            #create new data frame
            new_data = pd.DataFrame({
                "Timestamp": [timestamp],
                "Minutes":[minutes],
                "Sensor1": [pressure_1], 
                "Sensor2": [pressure_2], 
                "Units": [self.fyra_press_unit.get()],
                "TC1": [TC1],
                "TC2": [TC2],
                "TC3": [TC3],
                "TC4": [TC4],
                "Forward_Power1":[self.comet1_power_fwd.get()],
                "Reflected_Power1":[self.comet1_power_ref.get()],
                "Load_Pos1":[self.comet1_cap_load.get()],
                "Tune_Pos1":[self.comet1_cap_tune.get()],
                "Forward_Power2":[self.comet2_power_fwd.get()],
                "Reflected_Power2":[self.comet2_power_ref.get()],
                "Load_Pos2":[self.comet2_cap_load.get()],
                "Tune_Pos2":[self.comet2_cap_tune.get()],
                "Phase2":[self.comet2_phase.get()]
                })

            # Clean the data to avoid future warning about NA columns
            new_data.dropna(how='all', axis=1, inplace=True)
        
            # Concatenate new data ensuring no all-NA columns are included
            self.data = pd.concat([self.data, new_data], ignore_index=True)
                    
            # Append new data row directly to the file
            if self.record == True:
                self.save_data(new_data)
                
            self.update_plot()

        except Exception as e:
            print(f"Error parsing data: {e}")
            print(line)


    def update_plot(self):
        
        self.line_press_1.set_data(self.data['Minutes'], self.data['Sensor1'])
        self.line_press_2.set_data(self.data['Minutes'], self.data['Sensor2'])
        self.ax_press_1.set_ylabel(f" Sensor 1 {self.fyra_press_unit.get()}", color='b')
        self.ax_press_2.set_ylabel(f"Sensor 2 {self.fyra_press_unit.get()}", color='r')
        self.ax_press_1.relim()
        self.ax_press_1.autoscale_view()
        self.ax_press_1.autoscale()
        self.ax_press_2.relim()
        self.ax_press_2.autoscale_view()
        self.ax_press_2.autoscale()
        
        x_min = float(self.x_min_var.get()) if self.x_min_var.get() else None
        x_max = float(self.x_max_var.get()) if self.x_max_var.get() else None
        y1_min = float(self.y1_min_var.get()) if self.y1_min_var.get() else None
        y1_max = float(self.y1_max_var.get()) if self.y1_max_var.get() else None
        y2_min = float(self.y2_min_var.get()) if self.y2_min_var.get() else None
        y2_max = float(self.y2_max_var.get()) if self.y2_max_var.get() else None
        
        if x_min is not None and x_max is not None:
            self.ax_press_1.set_xlim([x_min, x_max])
            
        if y1_min is not None and y1_max is not None:
            if y1_min <=0:
                y1_min=1e-8            
            self.ax_press_1.set_ylim([y1_min, y1_max])
            
        if y2_min is not None and y2_max is not None:
            if y2_min <=0:
                y2_min=1e-8
            self.ax_press_2.set_ylim([y2_min, y2_max])
        
        if self.log_plot==True:
            self.ax_press_1.set_yscale('log')
            self.ax_press_2.set_yscale('log')
        else:
            self.ax_press_1.set_yscale('linear')
            self.ax_press_2.set_yscale('linear')
            
        #update temperature plot
        self.line_tc_1.set_data(self.data['Minutes'], self.data['TC1'])
        self.line_tc_2.set_data(self.data['Minutes'], self.data['TC2'])
        self.line_tc_3.set_data(self.data['Minutes'], self.data['TC3'])
        self.lineTC4.set_data(self.data['Minutes'], self.data['TC4'])
        self.ax_tc.relim()
        self.ax_tc.autoscale_view()
        self.ax_tc.autoscale()
        if x_min is not None and x_max is not None:
            self.ax_tc.set_xlim([x_min, x_max])

        #update power plot
        self.line_power_fwd1.set_data(self.data['Minutes'], self.data['Forward_Power1'])
        self.line_power_ref1.set_data(self.data['Minutes'], self.data['Reflected_Power1'])
        self.line_power_fwd2.set_data(self.data['Minutes'], self.data['Forward_Power2'])
        self.line_power_ref2.set_data(self.data['Minutes'], self.data['Reflected_Power2'])
                
        self.ax_power_fwd.relim()
        self.ax_power_fwd.autoscale_view()
        self.ax_power_fwd.autoscale()
        self.ax_power_ref.relim()
        self.ax_power_ref.autoscale_view()
        self.ax_power_ref.autoscale()
        if x_min is not None and x_max is not None:
            self.ax_power_fwd.set_xlim([x_min, x_max])
        
        #update Cap plots      
        self.line_cap_tune1.set_data(self.data['Minutes'], self.data['Tune_Pos1'])
        self.line_cap_load1.set_data(self.data['Minutes'], self.data['Load_Pos1'])
        self.line_cap_tune2.set_data(self.data['Minutes'], self.data['Tune_Pos2'])
        self.line_cap_load2.set_data(self.data['Minutes'], self.data['Load_Pos2'])
        self.ax_cap.relim()
        self.ax_cap.autoscale_view()
        self.ax_cap.autoscale()
        if x_min is not None and x_max is not None:
            self.ax_cap.set_xlim([x_min, x_max])
        
        self.canvas.draw()
        



#    #simple variable to enable data saving    
    def save_data(self,line_data):
        # Construct the file name with today's date
        date_str = datetime.now().strftime("%Y%m%d")
        filename = f"chamber_pressure_{date_str}.csv"

        # Check if the file already exists to decide on writing the header
        try:
            with open(filename, 'a', newline='') as file:
                writer = csv.writer(file)
                # Move the file pointer to the beginning and check if the file is empty
                file.seek(0, 2)  # Move the file pointer to the end of the file
                if file.tell() == 0:  # If file is empty, write the header
                    writer.writerow(['Timestamp', 'Minutes', 'Sensor1', 'Sensor2', 'Units','TC1','TC2','TC3','TC4',"Forward_Power1","Reflected_Power1", "Load_Pos1", "Tune_Pos1","Forward_Power2","Reflected_Power2", "Load_Pos2", "Tune_Pos2","Phase2"])
        except Exception as e:
            print(f"Error writing data to CSV: {e}")
        
        try:
            line_data.to_csv(filename,header=False, index=False, mode='a')
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save data: {e}")
         
    #set RF power     
    def set_power1(self):
        """Set the power setpoint by sending the write command to command 1206."""
        try:
            setpoint_w = float(self.comet1_power_set_new.get())  # Get power setpoint from user input (W)
            setpoint_data = int(setpoint_w * 1000)  # Convert W to mW by multiplying by 1000
            result = self.comet1.send_modbus_write_command(command_number=1206, data=setpoint_data)
            if result is not None:
                print(f"Set Power Setpoint command successful, response: {result}")
            else:
                print("Failed to send Set Power Setpoint command.")
        except ValueError:
            print("Invalid input. Please enter a valid number for the setpoint.")
    
    #set RF power     
    def set_power2(self):
        """Set the power setpoint by sending the write command to command 1206."""
        try:
            setpoint_w = float(self.comet2_power_set_new.get())  # Get power setpoint from user input (W)
            setpoint_data = int(setpoint_w * 1000)  # Convert W to mW by multiplying by 1000
            result = self.comet2.send_modbus_write_command(command_number=1206, data=setpoint_data)
            if result is not None:
                print(f"Set Power Setpoint command successful, response: {result}")
            else:
                print("Failed to send Set Power Setpoint command.")
        except ValueError:
            print("Invalid input. Please enter a valid number for the setpoint.")    

    #get phase     
    def set_phase2(self):
        """Set the power setpoint by sending the write command to command 1206."""
        try:
            setpoint_w = float(self.comet2_phase_set.get())  # Get power setpoint from user input (W)
            setpoint_data = int(setpoint_w)     
            result = self.comet2.send_modbus_write_command(command_number=1112, data=setpoint_data)
            if result is not None:
                print(f"Set Phase Setpoint command successful, response: {result}")
            else:                print("Failed to send Set Phase Setpoint command.")
        except ValueError:
            print("Invalid input. Please enter a valid number for the setpoint.")    
    
    #set tune capacitor position        
    def set_tune_cap1(self):
        """Set the tune capacitor position via command 9203."""
        try:
            tune_cap_position = int(self.comet1_cap_tune_set.get()*10)  # Get tune capacitor position in %
            if 0 <= tune_cap_position <= 1000:
                tune_cap_data = int(tune_cap_position)  # Ensure it's an integer
                result = self.comet1.send_modbus_write_command(command_number=8204, data=tune_cap_data)
                if result is not None:
                    print(f"Set Tune Capacitor command successful, response: {result}")
                else:
                    print("Failed to send Set Tune Capacitor command.")
            else:
                print("Invalid position. Please enter a value between 0 and 100.")
        except ValueError:
            print("Invalid input. Please enter a valid number for the tune capacitor position.")
   
    #set tune capacitor position        
    def set_tune_cap2(self):
        """Set the tune capacitor position via command 9203."""
        try:
            tune_cap_position = int(self.comet2_cap_tune_set.get()*10)  # Get tune capacitor position in %
            if 0 <= tune_cap_position <= 1000:
                tune_cap_data = int(tune_cap_position)  # Ensure it's an integer
                result = self.comet2.send_modbus_write_command(command_number=8204, data=tune_cap_data)
                if result is not None:
                    print(f"Set Tune Capacitor command successful, response: {result}")
                else:
                    print("Failed to send Set Tune Capacitor command.")
            else:
                print("Invalid position. Please enter a value between 0 and 100.")
        except ValueError:
            print("Invalid input. Please enter a valid number for the tune capacitor position.")            
            
    #set load capacitor position
    def set_load_cap1(self):
        """Set the load capacitor position via command 9204."""
        try:
            load_cap_position = int(self.comet1_cap_load_set.get()*10) # Get load capacitor position in %
            if 0 <= load_cap_position <= 1000:
                load_cap_data = int(load_cap_position)  # Ensure it's an integer
                result = self.comet1.send_modbus_write_command(command_number=8203, data=load_cap_data)
                if result is not None:
                    print(f"Set Load Capacitor command successful, response: {result}")
                else:
                    print("Failed to send Set Load Capacitor command.")
            else:
                print("Invalid position. Please enter a value between 0 and 100.")
        except ValueError:
            print("Invalid input. Please enter a valid number for the load capacitor position.")
    
    #set load capacitor position
    def set_load_cap2(self):
        """Set the load capacitor position via command 9204."""
        try:
            load_cap_position = int(self.comet2_cap_load_set.get()*10) # Get load capacitor position in %
            if 0 <= load_cap_position <= 1000:
                load_cap_data = int(load_cap_position)  # Ensure it's an integer
                result = self.comet2.send_modbus_write_command(command_number=8203, data=load_cap_data)
                if result is not None:
                    print(f"Set Load Capacitor command successful, response: {result}")
                else:
                    print("Failed to send Set Load Capacitor command.")
            else:
                print("Invalid position. Please enter a value between 0 and 100.")
        except ValueError:
            print("Invalid input. Please enter a valid number for the load capacitor position.")       
   
    #turn RF on
    def rf_on1(self):
        """Send the command to turn RF on."""
        result = self.comet1.send_modbus_write_command(command_number=1001, data=1)
        if result is not None:
            print(f"RF On command successful, response: {result}")
        else:
            print("Failed to send RF On command.")
    
    #turn RF on
    def rf_on2(self):
        """Send the command to turn RF on."""
        result = self.comet2.send_modbus_write_command(command_number=1001, data=1)
        if result is not None:
            print(f"RF On command successful, response: {result}")
        else:
            print("Failed to send RF On command.")    
    
    #turn RF off
    def rf_off1(self):
        """Send the command to turn RF off."""
        result = self.comet1.send_modbus_write_command(command_number=1001, data=0)
        if result is not None:
            print(f"RF Off command successful, response: {result}")
        else:
            print("Failed to send RF Off command.")
   
    #turn RF off
    def rf_off2(self):
        """Send the command to turn RF off."""
        result = self.comet2.send_modbus_write_command(command_number=1001, data=0)
        if result is not None:
            print(f"RF Off command successful, response: {result}")
        else:
            print("Failed to send RF Off command.")
        
    
    #turn on manual matching mode
    def manual_match1(self):
        """Set the matching mode to Manual (command 8201, data=1)."""
        result = self.comet1.send_modbus_write_command(command_number=8201, data=1)
        if result is not None:
            print(f"Set Manual Mode command successful, response: {result}")
        else:
            print("Failed to send Set Manual Mode command.")

    #turn on manual matching mode
    def manual_match2(self):
        """Set the matching mode to Manual (command 8201, data=1)."""
        result = self.comet2.send_modbus_write_command(command_number=8201, data=1)
        if result is not None:
            print(f"Set Manual Mode command successful, response: {result}")
        else:
            print("Failed to send Set Manual Mode command.")

    #turn on auto matching mode
    def auto_match1(self):
        """Set the matching mode to Auto (command 8201, data=2)."""
        result = self.comet1.send_modbus_write_command(command_number=8201, data=2)
        if result is not None:
            print(f"Set Auto Mode command successful, response: {result}")
        else:
            print("Failed to send Set Auto Mode command.")

    #turn on auto matching mode
    def auto_match2(self):
        """Set the matching mode to Auto (command 8201, data=2)."""
        result = self.comet2.send_modbus_write_command(command_number=8201, data=2)
        if result is not None:
            print(f"Set Auto Mode command successful, response: {result}")
        else:
            print("Failed to send Set Auto Mode command.")
    
    #send manual rf read command
    def rf_read1(self):
        print(self.comet1_command_type.get())
        if self.comet1_command_type.get()=='s':    
            result = self.comet1.send_modbus_read_command(command_number=int(self.comet1_command_number.get()), response_type='string')
        if self.comet1_command_type.get()=='i':    
            result = self.comet1.send_modbus_read_command(command_number=int(self.comet1_command_number.get()), response_type='integer')    
        if result is not None:
            print(f"RF read command successful, response: {result}")
            self.comet1_command_response.set(result)
        else:
            print("Failed to send RF read command. Please use 's' when expecting strings and 'i' when expecting integers.")

    #send manual rf read command
    def rf_read2(self):
        print(self.comet2_command_type.get())
        if self.comet2_command_type.get()=='s':    
            result = self.comet1.send_modbus_read_command(command_number=int(self.comet2_command_number.get()), response_type='string')
        if self.comet2_command_type.get()=='i':    
            result = self.comet1.send_modbus_read_command(command_number=int(self.comet2_command_number.get()), response_type='integer')    
        if result is not None:
            print(f"RF read command successful, response: {result}")
            self.comet2_command_response.set(result)
        else:
            print("Failed to send RF read command. Please use 's' when expecting strings and 'i' when expecting integers.")
    
    
    #send manual rf write command    
    def rf_write1(self):
        result = self.comet1.send_modbus_write_command(command_number=int(self.comet1_command_number.get()), data=int(self.comet_command_data.get()))
        if result is not None:
            print(f"RF write command successful, response: {result}")
            self.comet1_command_response.set(result)
        else:
            print("Failed to send RF write command.")

    #send manual rf write command    
    def rf_write2(self):
        result = self.comet2.send_modbus_write_command(command_number=int(self.comet2_command_number.get()), data=int(self.comet_command_data.get()))
        if result is not None:
            print(f"RF write command successful, response: {result}")
            self.comet2_command_response.set(result)
        else:
            print("Failed to send RF write command.")            
    
        
    #defin actions on closing      
    def on_closing(self):
        if self.fyra is not None:
            self.disable_control()
            self.fyra.close()
        if self.data_listener_thread is not None:
            self.data_listener_thread.join()
        if self.running is not None:    
            self.running.clear()
        self.root.destroy()
        
#start the gui
if __name__ == "__main__":
    root = tk.Tk()
    app = PressureControllerApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

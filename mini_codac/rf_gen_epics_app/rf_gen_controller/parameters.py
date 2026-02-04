
import logging

# Network stuff
DEFAULT_IP_ADDR  = "192.168.0.150"
DEFAULT_TCP_PORT = 502

# A description of the command numbers in CMDS can be found in the Cito Plus
# user manual "Air Cooled RF Generator cito and cito Plus" starting on page 262.
CMDS = {"get_ip":(5100, "bytes"), "get_date":(7102, "str"),
        "ctrl_src":(7002, "int"), "power_set_point":(1206, "int"),
        "state":(8000, "int"), "rf":(1001, "int"), "fwd_pwr":(8021, "int"),
        "rfl_pwr":(8022, "int"), "read_load_cap":(9203, "int"),
        "read_tune_cap":(9204, "int"), "move_load_cap":(8203, "int"),
        "move_tune_cap":(8204, "int"), "match_mode":(8201, "int"),
        "hostname":(5105, "str"), "domain_name":(5106, "str"),
        "phase_shift":(1112, "int")}

MAX_POWER = 999 # mili-Watts
MIN_POWER = 1000000 # mili-Watts


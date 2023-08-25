#!/usr/bin/env python3

# Based on official Nuclear Instruments N1081B SDK: https://github.com/NuclearInstruments/N1081B-SDK-Python.git

import os
import pprint
import time
from N1081B_sdk import N1081B

DEBUG = False

import configparser
config=configparser.ConfigParser()
config_file = os.path.realpath(__file__).replace(os.path.basename(__file__),'N1081B.ini')
config.read(config_file)

section_text = config["GLOBAL"].get("section", fallback='')
sections_applicable = [s for s in N1081B.Section if str(s) == 'Section.SEC_'+section_text]
section = sections_applicable[0] if len(sections_applicable) else N1081B.Section.SEC_D
section_scaler_text = config["GLOBAL"].get("section_scaler", fallback='')
sections_scaler_applicable = [s for s in N1081B.Section if str(s) == 'Section.SEC_'+section_scaler_text]
section_scaler = sections_applicable[0] if len(sections_scaler_applicable) else N1081B.Section.SEC_C
scaler_work_enabled = section_scaler_text != ''
if scaler_work_enabled:
  print('"Mute scaler" option is enabled')

pp = pprint.PrettyPrinter(indent=4)

# create N1081B board object
ipaddr = config["GLOBAL"].get("ip", fallback='')
if not ipaddr:
  print('No ip address!!!')
  exit(0)
N1081B_device = N1081B(ipaddr)
# connect to the board
N1081B_device.connect()

# get board information and print them
version_json = N1081B_device.get_version()
pp.pprint(version_json)
serial_number = version_json["data"]["serial_number"]
software_version = version_json["data"]["software_version"]
zynq_version = version_json["data"]["zynq_version"]
fpga_version = version_json["data"]["fpga_version"]

time.sleep(0.5) # 0.5 or 1.0

if scaler_work_enabled:
  # Disable scaler input
  resp = N1081B_device.configure_scaler(section_scaler, 500, False, True, True, True, False)
  if DEBUG:
    pp.pprint(resp)

# # set input of section D in NIM standard
# N1081B_device.set_input_configuration(section,
#                                       N1081B.SignalStandard.STANDARD_NIM,
#                                       N1081B.SignalStandard.STANDARD_NIM,
#                                       0, N1081B.SignalImpedance.IMPEDANCE_50)

# set output of section D in TTL or NIM standard
# N1081B_device.set_output_configuration(section, N1081B.SignalStandard.STANDARD_TTL)
# N1081B_device.set_output_configuration(section, N1081B.SignalStandard.STANDARD_NIM)
# set section D function as pulse generator
resp = N1081B_device.set_section_function(section, N1081B.FunctionType.FN_PULSE_GENERATOR)
if DEBUG:
  pp.pprint(resp)
# configure the pulse generator (normal random generator, width:200ns, period: 1s, output all enabled)
resp = N1081B_device.configure_pulse_generator(section, N1081B.StatisticMode.STAT_DETERMINISTIC,
                                        200, int(1e9), True, True, True, True)
if DEBUG:
  pp.pprint(resp)

time.sleep(2.0) # 2.0 or 20.0

# set output of section D in NIM standard
# N1081B_device.set_output_configuration(section, N1081B.SignalStandard.STANDARD_NIM)

# set section D function as rate meter
resp = N1081B_device.set_section_function(section, N1081B.FunctionType.FN_RATE_METER)
if DEBUG:
  pp.pprint(resp)
# configure the rate meter
resp = N1081B_device.configure_rate_meter(section, True, True, True, True, False)
if DEBUG:
  pp.pprint(resp)

if scaler_work_enabled:
  # Enable scaler input back
  resp = N1081B_device.configure_scaler(section_scaler, 500, True, True, True, True, False)
  if DEBUG:
    pp.pprint(resp)

# print current values rate meter values
counter_json = N1081B_device.get_function_results(section)
pp.pprint(counter_json)

# close connection
N1081B_device.disconnect()

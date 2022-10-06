#
# Testing a R&S VNA for basic PyVisa and SCPI communications
#
# VISA (Virtual Instrument Software Architecture) for Python
# PyVISA: https://pyvisa.readthedocs.io/en/latest/index.html
#
# RsInstrument is a Python remote-control communication module for R&S SCPI-based Test and Measurement Instruments
# https://pypi.org/project/RsInstrument
#
# Yujie Zhao, Physics & Astronomy, University of St. Andrews, Scotland
# DYK team, 05/10/2022
#

import numpy as np
import pyvisa  # find and download this library
from RsInstrument import *

# Test parameters you can change.
# If you do not know the IP address of your VNA, run and stop the program, and it will indicate the device IP.
# Put this address below (IPAddress = 'your IP address here')

FSTART = 0.5  # Start frequency in GHz
FSTOP = 3.0  # Stop frequency in GHz
FNUMP = 500  # Number of frequency points in a sweep
BWIF = 10000.0  # IF bandwidth in Hz
IFSEL = 'HIGH'  # Selectivity of IF receiver: NORMal | MEDium | HIGH
POWER = 0.0  # RF source power in dBm
AVERNUM = 3  # Number of frequency sweeps used to average a trace
AVERMODE = 'RED'  # AUTO/FLATten/REDuce/MOVing different averaging modes
AVERSTATE = 'ON'  # Averaging ON/OFF
VNAtimeout = 600000.0  # VNA's timeout (ms) should be sufficiently large to allow long operations

# An example of the test folder on your PC: 'C:\\Users\\PycharmProjects\\Tests'
PCFolder = 'your folder here'

# An example of the test folder on VNA: 'C:\\Users\\Public\\Documents\\Rohde-Schwarz\\Vna\\Tests'
VNAFolder = 'your folder here'

# An example of the device IP address: 'TCPIP0::169.254.90.230::inst0::INSTR'
IPAddress = 'your IP address here'

# The program will create the test s2p files for writing them to a VNA's folder
# and transferring as binary blocks directly to VNA's memory for de-embedding (if you have this option on your PC)

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# Do not change anything below this line
rm = pyvisa.ResourceManager()  # Recalling VISA drivers
print(rm.list_resources())  # List of the IP addresses of the devices connected to PC

VNA_RsInstr = RsInstrument(IPAddress)  # Initialisation of the session
VNA_RsInstr.opc_query_after_write = True  # Synchronisation after all "write"

for attempt in range(3):
    try:
        VNA = rm.open_resource(IPAddress)  # Connecting to VNA
    except NameError:
        print("Cant connect to device")

# Creating the test s2p files
Stimulus = []
for i in range(0, FNUMP):
    frequency = FSTART + ((FSTOP - FSTART) * i) / (FNUMP - 1)
    Stimulus.append(frequency)

ReS11_1 = []
ImS11_1 = []
ReS21_1 = []
ImS21_1 = []
ReS12_1 = []
ImS12_1 = []
ReS22_1 = []
ImS22_1 = []
for i in range(0, FNUMP):
    ReS11_1.append(-1.0)
    ImS11_1.append(0.0)
    ReS21_1.append(0.0)
    ImS21_1.append(0.0)
    ReS12_1.append(0.0)
    ImS12_1.append(0.0)
    ReS22_1.append(-1.0)
    ImS22_1.append(0.0)

ReS11_2 = ReS11_1
ImS11_2 = ImS11_1
ReS21_2 = ReS21_1
ImS21_2 = ImS21_1
ReS12_2 = ReS12_1
ImS12_2 = ImS12_1
ReS22_2 = ReS22_1
ImS22_2 = ImS22_1

AC1 = np.column_stack((Stimulus, ReS11_1, ImS11_1, ReS21_1, ImS21_1, ReS12_1, ImS12_1, ReS22_1, ImS22_1))
AC2 = np.column_stack((Stimulus, ReS11_2, ImS11_2, ReS21_2, ImS21_2, ReS12_2, ImS12_2, ReS22_2, ImS22_2))

# Saving s2p files on PC
np.savetxt(PCFolder + '\\TestFile_1.s2p', AC1, delimiter='\t', header='Hz S RI R 50.00')
np.savetxt(PCFolder + '\\TestFile_2.s2p', AC2, delimiter='\t', header='Hz S RI R 50.00')

VNA.write('*RST')  # Reset VNA to the default state
VNA.write(':SYSTEM:DISPLAY:UPDATE ON')  # Updating VNA's display
VNA.write('SYST:DISP:BAR:HKEY ON')  # Display hard keys
VNA.write('SWE:TYPE LIN')  # Linear sweep at a constant power
VNA.write('SWE:GEN STEP')  # Stepped sweep
VNA.write('INIT:CONT:ALL ON')  # Continuous frequency sweep
VNA.timeout = VNAtimeout

VAR = str(FSTART)  # Start frequency as a string
SCPI = ':FREQ:STAR ' + VAR + 'GHZ'
VNA.write(SCPI)

VAR = str(FSTOP)  # Stop frequency as a string
SCPI = ':FREQ:STOP ' + VAR + 'GHZ'
VNA.write(SCPI)

VAR = str(FNUMP)  # Number of frequency points as a string
SCPI = 'SWE:POIN ' + VAR
VNA.write(SCPI)

VAR = str(BWIF)  # Bendwidth as a string
SCPI = 'BAND ' + VAR
VNA.write(SCPI)

SCPI = 'BAND:RES:SEL ' + IFSEL  # IF selectivity as a string
VNA.write(SCPI)

VAR = str(POWER)  # Power as a string
SCPI = 'SOUR:POW ' + VAR
VNA.write(SCPI)

VAR = str(AVERNUM)  # Averaging number as a string
SCPI = 'AVER:COUN ' + VAR
VNA.write(SCPI)

SCPI = 'AVER:MODE ' + AVERMODE  # Averaging mode as a string
VNA.write(SCPI)

SCPI = 'AVER ' + AVERSTATE  # Averaging state YES/NO as a string
VNA.write(SCPI)

PCFullAddress1 = PCFolder + '\\TestFile_1.s2p'
PCFullAddress2 = PCFolder + '\\TestFile_2.s2p'
VNAFullAddress1 = VNAFolder + '\\TestFile_1.s2p'
VNAFullAddress2 = VNAFolder + '\\TestFile_2.s2p'

# Transferring s2p files from PC to VNA
VNA_RsInstr.send_file_from_pc_to_instrument(PCFullAddress1, VNAFullAddress1)
VNA_RsInstr.send_file_from_pc_to_instrument(PCFullAddress2, VNAFullAddress1)

# If you have the de-embedding option on your VNA, you could try transferring binary blocks. See below
# SCPI command for writing a .s2p file into the VNA's internal memory. The file is converted into a binary data block.
# FPOR - standard port sequence (network port 1 towards VNA, network port 2 towards DUT)
# SCPI1 = 'CALC1:TRAN:VNET:SEND:DEEM1:PAR:DATA FPOR, '
# VNA_RsInstr.write_bin_block_from_file(SCPI1, PCFullAddress1)
# SCPI2 = 'CALC1:TRAN:VNET:SEND:DEEM2:PAR:DATA FPOR, '
# VNA_RsInstr.write_bin_block_from_file(SCPI2, PCFullAddress2)
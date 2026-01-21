#!/usr/bin/env python3
"""
BeagleBone Black Cape EEPROM Generator

Generates a binary EEPROM image following the BeagleBoard cape specification.
See: https://docs.beagleboard.org/boards/beaglebone/black/ch08.html
"""

import argparse
import struct
import datetime
import sys
from pathlib import Path

# EEPROM field sizes (bytes)
HEADER_SIZE = 4
EEPROM_REV_SIZE = 2
BOARD_NAME_SIZE = 32
VERSION_SIZE = 4
MANUFACTURER_SIZE = 16
PART_NUMBER_SIZE = 16
NUM_PINS_SIZE = 2
SERIAL_NUMBER_SIZE = 12
PIN_USAGE_SIZE = 148  # 74 pins * 2 bytes each
VDD_3V3B_SIZE = 2
VDD_5V_SIZE = 2
SYS_5V_SIZE = 2
DC_SUPPLIED_SIZE = 2

# Magic header bytes
EEPROM_HEADER = bytes([0xAA, 0x55, 0x33, 0xEE])

# Default values for BB-IO-CAPE
DEFAULTS = {
    'board_name': 'BB-IO-CAPE',
    'version': '0001',
    'manufacturer': 'Andrew C. Young',
    'part_number': 'BB-IO-CAPE-01',
    'eeprom_rev': 'A1',
    'vdd_3v3b_ma': 50,   # Estimated current draw in mA
    'vdd_5v_ma': 0,      # Not using 5V rail
    'sys_5v_ma': 0,      # Not using SYS_5V
    'dc_supplied_ma': 0, # Not supplying power
}


def pad_string(s: str, length: int) -> bytes:
    """Pad a string with spaces to the specified length."""
    encoded = s.encode('ascii')
    if len(encoded) > length:
        raise ValueError(f"String '{s}' exceeds maximum length of {length}")
    return encoded.ljust(length, b' ')


def generate_serial_number(assembly_code: str = 'CAPE') -> str:
    """
    Generate a serial number in the format WWYY&&&&nnnn.

    WW: Week of production (01-52)
    YY: Year of production (last two digits)
    &&&&: Assembly code (4 chars)
    nnnn: Board number (0001-9999)
    """
    now = datetime.datetime.now()
    week = now.isocalendar()[1]
    year = now.year % 100
    # Pad or truncate assembly code to 4 characters
    assembly = assembly_code[:4].ljust(4, '0')
    return f"{week:02d}{year:02d}{assembly}0001"

def build_pin_usage_data() -> bytes:
    """
    Build the pin usage data for the BB-IO-CAPE.

    Each pin is represented by 2 bytes (16 bits) in Big Endian:
    - Bit 15: Pin used (1) or not used (0)
    - Bits 14-7: Reserved (0)
    - Bit 6: Slew rate (0=fast, 1=slow)
    - Bit 5: RX enable (0=disabled, 1=enabled)
    - Bit 4: Pull up/down select (0=pulldown, 1=pullup)
    - Bit 3: Pull up/down enable (0=enabled, 1=disabled)
    - Bits 2-0: Mux mode (0-7)

    Pin index mapping:
    - P8 pins 1-46 -> indices 0-45
    - P9 pins 1-46 -> indices 46-91
    """
    # Initialize all 74 pins as unused (74 pins * 2 bytes = 148 bytes)
    pin_data = bytearray(PIN_USAGE_SIZE)

    def set_pin(header: int, pin: int, mux_mode: int = 7,
                rx_enable: bool = False, pullup: bool = True,
                pull_disable: bool = False, slew_slow: bool = False):
        """Set a pin as used with the specified configuration."""
        # Calculate index: P8 pins are 0-45, P9 pins are 46-91
        if header == 8:
            index = pin - 1
        else:  # header == 9
            index = 46 + (pin - 1)

        if index < 0 or index >= 74:
            return  # Skip invalid indices

        # Build the 16-bit value
        value = 0x8000  # Bit 15: pin used
        if slew_slow:
            value |= 0x0040  # Bit 6
        if rx_enable:
            value |= 0x0020  # Bit 5
        if pullup:
            value |= 0x0010  # Bit 4
        if pull_disable:
            value |= 0x0008  # Bit 3
        value |= (mux_mode & 0x07)  # Bits 2-0

        # Store as Big Endian
        pin_data[index * 2] = (value >> 8) & 0xFF
        pin_data[index * 2 + 1] = value & 0xFF

    # BB-IO-CAPE Pin Configuration (from README.md)
    #
    # UART1: P9/26 (RX), P9/24 (TX) - Mode 0
    set_pin(9, 26, mux_mode=0, rx_enable=True)   # UART1_RXD
    set_pin(9, 24, mux_mode=0)                    # UART1_TXD

    # UART2: P9/22 (RX), P9/21 (TX) - Mode 1
    set_pin(9, 22, mux_mode=1, rx_enable=True)   # UART2_RXD
    set_pin(9, 21, mux_mode=1)                    # UART2_TXD

    # UART4: P9/11 (RX), P9/13 (TX) - Mode 6
    set_pin(9, 11, mux_mode=6, rx_enable=True)   # UART4_RXD
    set_pin(9, 13, mux_mode=6)                    # UART4_TXD

    # I2C1: P9/17 (SCL), P9/18 (SDA) - Mode 2
    set_pin(9, 17, mux_mode=2, rx_enable=True)   # I2C1_SCL
    set_pin(9, 18, mux_mode=2, rx_enable=True)   # I2C1_SDA

    # I2C2: P9/19 (SCL), P9/20 (SDA) - Mode 3
    # Note: I2C2 is used for cape EEPROM, directly connected
    set_pin(9, 19, mux_mode=3, rx_enable=True)   # I2C2_SCL
    set_pin(9, 20, mux_mode=3, rx_enable=True)   # I2C2_SDA

    # Analog inputs (A1, A2, A3) - these only use bit 15 (used flag)
    # A1: P9/39 (AIN0), P9/33 (AIN4)
    set_pin(9, 39, mux_mode=0)  # AIN0
    set_pin(9, 33, mux_mode=0)  # AIN4
    # A2: P9/37 (AIN2), P9/35 (AIN6)
    set_pin(9, 37, mux_mode=0)  # AIN2
    set_pin(9, 35, mux_mode=0)  # AIN6
    # A3: P9/38 (AIN3), P9/36 (AIN5)
    set_pin(9, 38, mux_mode=0)  # AIN3
    set_pin(9, 36, mux_mode=0)  # AIN5

    # Digital GPIO connectors (D1-D9) - Mode 7 (GPIO)
    # D1: P9/42 (GPIO 07), P9/41 (GPIO 116)
    set_pin(9, 42, mux_mode=7)
    set_pin(9, 41, mux_mode=7)
    # D2: P8/19 (GPIO 22), P8/13 (GPIO 23)
    set_pin(8, 19, mux_mode=7)
    set_pin(8, 13, mux_mode=7)
    # D3: P8/14 (GPIO 26), P8/17 (GPIO 27)
    set_pin(8, 14, mux_mode=7)
    set_pin(8, 17, mux_mode=7)
    # D4: P8/12 (GPIO 44), P8/11 (GPIO 45)
    set_pin(8, 12, mux_mode=7)
    set_pin(8, 11, mux_mode=7)
    # D5: P8/16 (GPIO 46), P8/15 (GPIO 47)
    set_pin(8, 16, mux_mode=7)
    set_pin(8, 15, mux_mode=7)
    # D6: P9/15 (GPIO 48), P9/16 (GPIO 51)
    set_pin(9, 15, mux_mode=7)
    set_pin(9, 16, mux_mode=7)
    # D7: P8/7 (GPIO 66), P8/8 (GPIO 67)
    set_pin(8, 7, mux_mode=7)
    set_pin(8, 8, mux_mode=7)
    # D8: P8/10 (GPIO 68), P8/9 (GPIO 69)
    set_pin(8, 10, mux_mode=7)
    set_pin(8, 9, mux_mode=7)
    # D9: P9/25 (GPIO 117), P9/27 (GPIO 115)
    set_pin(9, 25, mux_mode=7)
    set_pin(9, 27, mux_mode=7)

    # RTC: P9/12 (GPIO 60), P8/28 (GPIO 88) - for RTC interrupt/output
    set_pin(9, 12, mux_mode=7)
    set_pin(8, 28, mux_mode=7)

    return bytes(pin_data)


def generate_eeprom(args) -> bytes:
    """Generate the complete EEPROM binary image."""
    data = bytearray()

    # Header (4 bytes) - Magic number
    data.extend(EEPROM_HEADER)

    # EEPROM Revision (2 bytes)
    data.extend(pad_string(args.eeprom_rev, EEPROM_REV_SIZE))

    # Board Name (32 bytes)
    data.extend(pad_string(args.board_name, BOARD_NAME_SIZE))

    # Version (4 bytes)
    data.extend(pad_string(args.version, VERSION_SIZE))

    # Manufacturer (16 bytes)
    data.extend(pad_string(args.manufacturer, MANUFACTURER_SIZE))

    # Part Number (16 bytes)
    data.extend(pad_string(args.part_number, PART_NUMBER_SIZE))

    # Number of Pins (2 bytes) - Big Endian
    # Count: 3 UARTs (6 pins) + 2 I2C (4 pins) + 3 Analog (6 pins)
    #      + 9 Digital (18 pins) + 1 RTC (2 pins) = 36 pins
    num_pins = 36
    data.extend(struct.pack('>H', num_pins))

    # Serial Number (12 bytes)
    serial = args.serial or generate_serial_number()
    data.extend(pad_string(serial, SERIAL_NUMBER_SIZE))

    # Pin Usage (148 bytes)
    data.extend(build_pin_usage_data())

    # VDD_3V3B Current (2 bytes) - Big Endian, in mA
    data.extend(struct.pack('>H', args.vdd_3v3b_ma))

    # VDD_5V Current (2 bytes) - Big Endian, in mA
    data.extend(struct.pack('>H', args.vdd_5v_ma))

    # SYS_5V Current (2 bytes) - Big Endian, in mA
    data.extend(struct.pack('>H', args.sys_5v_ma))

    # DC Supplied (2 bytes) - Big Endian, in mA
    data.extend(struct.pack('>H', args.dc_supplied_ma))

    return bytes(data)


def print_eeprom_info(data: bytes):
    """Print a human-readable summary of the EEPROM contents."""
    print("\nEEPROM Contents:")
    print("-" * 50)
    print(f"Header:       0x{data[0:4].hex().upper()}")
    print(f"EEPROM Rev:   {data[4:6].decode('ascii').strip()}")
    print(f"Board Name:   {data[6:38].decode('ascii').strip()}")
    print(f"Version:      {data[38:42].decode('ascii').strip()}")
    print(f"Manufacturer: {data[42:58].decode('ascii').strip()}")
    print(f"Part Number:  {data[58:74].decode('ascii').strip()}")
    print(f"Num Pins:     {struct.unpack('>H', data[74:76])[0]}")
    print(f"Serial:       {data[76:88].decode('ascii').strip()}")
    print(f"VDD_3V3B:     {struct.unpack('>H', data[236:238])[0]} mA")
    print(f"VDD_5V:       {struct.unpack('>H', data[238:240])[0]} mA")
    print(f"SYS_5V:       {struct.unpack('>H', data[240:242])[0]} mA")
    print(f"DC Supplied:  {struct.unpack('>H', data[242:244])[0]} mA")
    print(f"Total size:   {len(data)} bytes")
    print("-" * 50)


def main():
    parser = argparse.ArgumentParser(
        description='Generate BeagleBone Cape EEPROM binary image',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                          # Generate with defaults
  %(prog)s -o my_cape.bin           # Specify output file
  %(prog)s --serial 0325CAPE0042    # Specify serial number
        """
    )

    parser.add_argument('-o', '--output', type=str, default='cape_eeprom.bin',
                        help='Output filename (default: cape_eeprom.bin)')
    parser.add_argument('--board-name', type=str, default=DEFAULTS['board_name'],
                        help=f"Board name, max 32 chars (default: {DEFAULTS['board_name']})")
    parser.add_argument('--version', type=str, default=DEFAULTS['version'],
                        help=f"Hardware version, 4 chars (default: {DEFAULTS['version']})")
    parser.add_argument('--manufacturer', type=str, default=DEFAULTS['manufacturer'],
                        help=f"Manufacturer name, max 16 chars (default: {DEFAULTS['manufacturer']})")
    parser.add_argument('--part-number', type=str, default=DEFAULTS['part_number'],
                        help=f"Part number, max 16 chars (default: {DEFAULTS['part_number']})")
    parser.add_argument('--eeprom-rev', type=str, default=DEFAULTS['eeprom_rev'],
                        help=f"EEPROM revision, 2 chars (default: {DEFAULTS['eeprom_rev']})")
    parser.add_argument('--serial', type=str, default=None,
                        help='Serial number, 12 chars (default: auto-generated)')
    parser.add_argument('--vdd-3v3b-ma', type=int, default=DEFAULTS['vdd_3v3b_ma'],
                        help=f"VDD_3V3B current in mA (default: {DEFAULTS['vdd_3v3b_ma']})")
    parser.add_argument('--vdd-5v-ma', type=int, default=DEFAULTS['vdd_5v_ma'],
                        help=f"VDD_5V current in mA (default: {DEFAULTS['vdd_5v_ma']})")
    parser.add_argument('--sys-5v-ma', type=int, default=DEFAULTS['sys_5v_ma'],
                        help=f"SYS_5V current in mA (default: {DEFAULTS['sys_5v_ma']})")
    parser.add_argument('--dc-supplied-ma', type=int, default=DEFAULTS['dc_supplied_ma'],
                        help=f"DC supplied current in mA (default: {DEFAULTS['dc_supplied_ma']})")
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Print EEPROM contents after generation')

    args = parser.parse_args()

    # Generate the EEPROM data
    eeprom_data = generate_eeprom(args)

    # Write to file
    output_path = Path(args.output)
    output_path.write_bytes(eeprom_data)
    print(f"Generated EEPROM image: {output_path} ({len(eeprom_data)} bytes)")

    if args.verbose:
        print_eeprom_info(eeprom_data)

    # Always print a hex dump of the first 96 bytes (the identification data)
    print("\nFirst 96 bytes (hex):")
    for i in range(0, min(96, len(eeprom_data)), 16):
        hex_part = ' '.join(f'{b:02X}' for b in eeprom_data[i:i+16])
        ascii_part = ''.join(chr(b) if 32 <= b < 127 else '.' for b in eeprom_data[i:i+16])
        print(f"  {i:04X}: {hex_part:<48} |{ascii_part}|")


if __name__ == '__main__':
    main()

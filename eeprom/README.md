# BeagleBone Cape EEPROM Programming

This directory contains tools to program the identification EEPROM on the BB-IO-CAPE board.

## Overview

BeagleBone capes must have an EEPROM containing identification data so the BeagleBone can recognize and configure the cape during boot. The EEPROM stores:

- Board name and version
- Manufacturer information
- Serial number
- Pin configuration data
- Power requirements

## Hardware Setup

### EEPROM Details

| Parameter       | Value                                  |
|-----------------|----------------------------------------|
| Chip            | CAT24C256 (U1)                         |
| Capacity        | 256 Kbit (32 KB)                       |
| I2C Bus         | I2C-2 (P9 pins 19/20)                  |
| Write Protect   | TP1 (ground to enable writes)          |

### I2C Address Selection (SW1)

The DIP switch SW1 sets the EEPROM's I2C address:

| SW1 Position | A1  | A0  | I2C Address |
|--------------|-----|-----|-------------|
| All OFF      | 1   | 1   | 0x57        |
| A0 ON        | 1   | 0   | 0x56        |
| A1 ON        | 0   | 1   | 0x55        |
| A0+A1 ON     | 0   | 0   | 0x54        |

**Default:** All switches OFF = address 0x57

This allows up to 4 capes to be stacked, each with a unique address.

## Files

| File                | Description                                      |
|---------------------|--------------------------------------------------|
| `generate_eeprom.py` | Python script to generate the EEPROM binary      |
| `write_eeprom.sh`    | Shell script to program EEPROM on BeagleBone     |
| `cape_eeprom.bin`    | Generated EEPROM binary image (after running py) |

## Usage

### Step 1: Generate the EEPROM Image

Run on any computer with Python 3:

```bash
# Generate with default settings
python3 generate_eeprom.py

# Generate with custom options
python3 generate_eeprom.py --serial 0125CAPE0001 -v

# See all options
python3 generate_eeprom.py --help
```

This creates `cape_eeprom.bin`.

### Step 2: Copy Files to BeagleBone

Copy both the binary and the write script to your BeagleBone:

```bash
scp cape_eeprom.bin write_eeprom.sh debian@beaglebone.local:~
```

### Step 3: Program the EEPROM

On the BeagleBone, with the cape attached:

```bash
sudo ./write_eeprom.sh cape_eeprom.bin
```

The script will:

1. Prompt you to ground TP1 (Write Protect)
2. Detect the EEPROM address automatically
3. Write the binary data to the EEPROM
4. Verify the write was successful
5. Prompt you to disconnect TP1

### Step 4: Verify Cape Detection

Reboot the BeagleBone and verify the cape is detected:

```bash
# Check cape manager slots
cat /sys/devices/platform/bone_capemgr/slots

# Check kernel messages
dmesg | grep -i cape

# Read EEPROM directly
hexdump -C /sys/bus/i2c/devices/2-0057/eeprom | head -10
```

## EEPROM Data Format

The EEPROM follows the BeagleBoard cape specification:

| Offset | Size | Field            | Default Value            |
|--------|------|------------------|--------------------------|
| 0      | 4    | Magic Header     | 0xAA5533EE               |
| 4      | 2    | EEPROM Revision  | A1                       |
| 6      | 32   | Board Name       | BB-IO-CAPE               |
| 38     | 4    | Version          | 0001                     |
| 42     | 16   | Manufacturer     | Andrew C. Young          |
| 58     | 16   | Part Number      | BB-IO-CAPE-01            |
| 74     | 2    | Number of Pins   | 0                        |
| 76     | 12   | Serial Number    | WWYYCAPE0001             |
| 88     | 148  | Pin Usage        | (zeros)                  |
| 236    | 2    | VDD_3V3B Current | 50 mA                    |
| 238    | 2    | VDD_5V Current   | 0 mA                     |
| 240    | 2    | SYS_5V Current   | 0 mA                     |
| 242    | 2    | DC Supplied      | 0 mA                     |

## Troubleshooting

### EEPROM not detected

1. Check that the cape is properly seated on the headers
2. Verify SW1 DIP switch position
3. Scan the I2C bus manually:

   ```bash
   sudo i2cdetect -y -r 2
   ```

   The EEPROM should appear at 0x54, 0x55, 0x56, or 0x57.

### Write fails / verification fails

1. Ensure TP1 is properly grounded to TP2
2. Check for loose connections
3. Try a slower write by modifying the dd block size in the script

### Cape not detected after reboot

1. Verify the magic header is correct: first 4 bytes should be `AA 55 33 EE`
2. Check that the board name starts with a valid prefix
3. Review `dmesg` for cape-related errors

## References

- [BeagleBoard Cape Support Documentation](https://docs.beagleboard.org/boards/beaglebone/black/ch08.html)
- [CAT24C256 Datasheet](https://www.onsemi.com/pdf/datasheet/cat24c256-d.pdf)
- [BBCape_EEPROM Tool](https://github.com/beagleboard/BBCape_EEPROM)

#!/bin/bash
#
# BeagleBone Black Cape EEPROM Programmer
#
# This script programs the cape EEPROM directly on the BeagleBone Black.
# Run this script on the BBB with the cape attached.
#
# Usage: sudo ./write_eeprom.sh [eeprom_file] [address]
#   eeprom_file: Path to the binary EEPROM image (default: cape_eeprom.bin)
#   address: I2C address 0x54-0x57 (default: auto-detect)
#

set -e

# Default values
EEPROM_FILE="${1:-cape_eeprom.bin}"
I2C_BUS="2"
DEVICE_TYPE="24c256"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    error "This script must be run as root. Use: sudo $0"
fi

# Check if EEPROM file exists
if [ ! -f "$EEPROM_FILE" ]; then
    error "EEPROM file not found: $EEPROM_FILE"
fi

EEPROM_SIZE=$(stat -c%s "$EEPROM_FILE")
info "EEPROM file: $EEPROM_FILE ($EEPROM_SIZE bytes)"

# Detect or use specified address
if [ -n "$2" ]; then
    I2C_ADDR="$2"
    info "Using specified address: $I2C_ADDR"
else
    info "Scanning for cape EEPROM on I2C bus $I2C_BUS..."

    # Try to detect EEPROM at addresses 0x54-0x57
    FOUND_ADDR=""
    for addr in 54 55 56 57; do
        if i2cdetect -y -r $I2C_BUS 0x$addr 0x$addr 2>/dev/null | grep -q "$addr"; then
            FOUND_ADDR="0x$addr"
            break
        fi
    done

    if [ -z "$FOUND_ADDR" ]; then
        warn "No EEPROM detected at addresses 0x54-0x57"
        warn "Make sure:"
        warn "  1. The cape is properly connected"
        warn "  2. SW1 DIP switch is set correctly"
        echo ""
        echo "Available I2C devices on bus $I2C_BUS:"
        i2cdetect -y -r $I2C_BUS
        echo ""
        read -p "Enter EEPROM address manually [0x55]: " I2C_ADDR
        if [ -z "$I2C_ADDR" ]; then
            I2C_ADDR="0x55"
            info "Using default address: $I2C_ADDR"
        fi
    else
        I2C_ADDR="$FOUND_ADDR"
        info "Found EEPROM at address: $I2C_ADDR"
    fi
fi

# Convert address for sysfs path (e.g., 0x57 -> 0057)
ADDR_NUM="${I2C_ADDR#0x}"
SYSFS_ADDR="00${ADDR_NUM}"
DEVICE_PATH="/sys/bus/i2c/devices/${I2C_BUS}-${SYSFS_ADDR}"
EEPROM_PATH="${DEVICE_PATH}/eeprom"

echo ""
echo "=============================================="
echo "  BeagleBone Cape EEPROM Programmer"
echo "=============================================="
echo ""
echo "  EEPROM File:  $EEPROM_FILE"
echo "  I2C Bus:      $I2C_BUS"
echo "  I2C Address:  $I2C_ADDR"
echo "  Device Path:  $EEPROM_PATH"
echo ""

# Step 1: Ground the write protect pin
echo -e "${YELLOW}IMPORTANT: Write Protection${NC}"
echo ""
echo "  Before programming, you must GROUND the Write Protect test point (TP1)."
echo "  Connect TP1 to TP2 (GND) using a jumper wire or tweezers."
echo ""
read -p "Press Enter when TP1 is grounded... "

# Step 2: Create device node if it doesn't exist
if [ ! -d "$DEVICE_PATH" ]; then
    info "Creating I2C device node..."
    echo "$DEVICE_TYPE ${I2C_ADDR}" > /sys/bus/i2c/devices/i2c-${I2C_BUS}/new_device
    sleep 0.5

    if [ ! -d "$DEVICE_PATH" ]; then
        error "Failed to create device node at $DEVICE_PATH"
    fi
fi

if [ ! -f "$EEPROM_PATH" ]; then
    error "EEPROM sysfs file not found at $EEPROM_PATH"
fi

info "Device node ready: $EEPROM_PATH"

# Step 3: Write the EEPROM data
info "Writing EEPROM data..."
if dd if="$EEPROM_FILE" of="$EEPROM_PATH" bs=1 2>/dev/null; then
    info "Write completed successfully"
else
    error "Failed to write EEPROM data"
fi

# Step 4: Verify the write
info "Verifying EEPROM contents..."
TEMP_FILE=$(mktemp)
dd if="$EEPROM_PATH" of="$TEMP_FILE" bs=1 count="$EEPROM_SIZE" 2>/dev/null

if cmp -s "$EEPROM_FILE" "$TEMP_FILE"; then
    info "Verification PASSED - EEPROM contents match"
else
    rm -f "$TEMP_FILE"
    error "Verification FAILED - EEPROM contents do not match!"
fi
rm -f "$TEMP_FILE"

# Step 5: Display the written data
echo ""
info "EEPROM contents (first 96 bytes):"
hexdump -C "$EEPROM_PATH" | head -6

# Step 6: Remove write protection
echo ""
echo -e "${YELLOW}IMPORTANT: Re-enable Write Protection${NC}"
echo ""
echo "  Programming complete! Now REMOVE the ground connection from TP1."
echo "  This will re-enable write protection to prevent accidental overwrites."
echo ""
read -p "Press Enter when TP1 is disconnected from ground... "

# Done
echo ""
echo -e "${GREEN}=============================================="
echo "  EEPROM Programming Complete!"
echo "==============================================${NC}"
echo ""
echo "  The cape EEPROM has been programmed successfully."
echo ""
echo "  To verify cape detection, reboot the BeagleBone and run:"
echo "    dmesg | grep -i cape"
echo ""

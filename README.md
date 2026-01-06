# BeagleBone Black I/O Cape

A KiCad-designed I/O expansion cape for the BeagleBone Black SBC, featuring Grove-compatible connectors for easy interfacing with sensors, actuators, and communication peripherals.

**NOTE: The design has not yet been verified, use at your own risk!**

![schematic](schematic.png) ![PCB mockup](pcb.png)

## Features

| Interface | Connector Count | Notes                           |
|-----------|----------------:|---------------------------------|
| Analog    |               3 | Grove 4-pin (A1, A2, A3)        |
| Digital   |               9 | Grove 4-pin (D1-D9)             |
| I2C       |               2 | Grove 4-pin (I2C1, I2C2)        |
| UART      |               3 | Grove 4-pin (GPS, Rotator, Radio) |

### Onboard Components

- **DS3231MZ** - High-precision real-time clock with CR2032 battery backup
- **CAT24C256** - 256Kb I2C EEPROM for cape identification
- **2-position DIP switch** - Configuration options
- **Test points** - WP (write protect) and GND

## Pinout

The cape connects via the standard BeagleBone Black P8 and P9 expansion headers (2x23 pin, 2.54mm pitch).

## Manufacturing

Production files (Gerbers, BOM, pick-and-place positions) can be generated using KiCad's fabrication toolkit or found in the `production/` directory.

### BOM Summary

| Component     | Value/Part   | Quantity |
|---------------|--------------|----------|
| Grove 4-pin   | Vertical     | 17       |
| EEPROM        | CAT24C256    | 1        |
| RTC           | DS3231MZ     | 1        |
| Battery       | CR2032       | 1        |
| DIP Switch    | 2-position   | 1        |
| Capacitors    | 100nF 0603   | 2        |
| Resistors     | 10kΩ 0603    | 2        |
| Resistor Array| 10kΩ 4x0603  | 1        |
| Resistor Array| 5.6kΩ 4x0603 | 1        |

## Requirements

- KiCad 8.0 or later
- BeagleBone Black (or compatible: BBB Wireless, BeagleBone AI, etc.)

## License

[Add your license here]

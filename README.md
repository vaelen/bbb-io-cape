# BeagleBone Black I/O Cape

A KiCad-designed I/O expansion cape for the BeagleBone Black SBC, featuring Grove-compatible connectors for easy interfacing with sensors, actuators, and communication peripherals.

**NOTE: The design has not yet been verified, use at your own risk!**

![schematic](schematic.png) ![PCB mockup](pcb.png)

## Features

| Interface | Connector Count | Notes                             |
|-----------|----------------:|-----------------------------------|
| Analog    |               3 | Grove 4-pin (A1, A2, A3)          |
| Digital   |               9 | Grove 4-pin (D1-D9)               |
| I2C       |               2 | Grove 4-pin (I2C1, I2C2)          |
| UART      |               3 | Grove 4-pin (UART1, UART2, UART4) |

### Onboard Components

- **DS3231MZ** - High-precision real-time clock with CR2032 battery backup
- **CAT24C256** - 256Kb I2C EEPROM for cape identification
- **2-position DIP switch** - Configuration options
- **Test points** - WP (write protect) and GND

## Pinout

The cape connects via the standard BeagleBone Black P8 and P9 expansion headers (2x23 pin, 2.54mm pitch).

### Connectors

| Connector | Pin 1   | Pin 2   | Function            |
|-----------|---------|---------|---------------------|
| UART1     | P9 / 26 | P9 / 24 | UART1 RX / TX       |
| UART2     | P9 / 22 | P9 / 21 | UART2 RX / TX       |
| UART4     | P9 / 11 | P9 / 13 | UART4 RX / TX       |
| I2C1      | P9 / 17 | P9 / 18 | I2C1 SCL / SDA      |
| I2C2      | P9 / 19 | P9 / 20 | I2C2 SCL / SDA      |
| A1        | P9 / 39 | P9 / 33 | AIN 0 / AIN 4       |
| A2        | P9 / 37 | P9 / 35 | AIN 2 / AIN 6       |
| A3        | P9 / 38 | P9 / 36 | AIN 3 / AIN 5       |
| D1        | P9 / 42 | P9 / 41 | GPIO 07 / GPIO 116  |
| D2        | P8 / 19 | P8 / 13 | GPIO 22 / GPIO 23   |
| D3        | P8 / 14 | P8 / 17 | GPIO 26 / GPIO 27   |
| D4        | P8 / 12 | P8 / 11 | GPIO 44 / GPIO 45   |
| D5        | P8 / 16 | P8 / 15 | GPIO 46 / GPIO 47   |
| D6        | P9 / 15 | P9 / 16 | GPIO 48 / GPIO 51   |
| D7        | P8 / 7  | P8 / 8  | GPIO 66 / GPIO 67   |
| D8        | P8 / 10 | P8 / 9  | GPIO 68 / GPIO 69   |
| D9        | P9 / 25 | P9 / 27 | GPIO 117 / GPIO 115 |
| RTC       | P9 / 12 | P8 / 28 | GPIO 60 / GPIO 88   |

**Note:** All I/O signals are 3.3V. Do not apply 5V to any I/O pin.

## Real Time Clock

The real time clock is wired into the I2C2 bus as device 0x68.

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

MIT License

Copyright (c) 2026, Andrew C. Young

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

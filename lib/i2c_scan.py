#!/usr/bin/env python3
"""Scan all I2C buses and report known device addresses."""

import glob
import os
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from config import Config

KNOWN_DEVICES = {
    0x25: "I2C-CAN (Seeed/Longan MCP2515)",
    0x3E: "LCD1602 (typical)",
    0x27: "LCD1602 (alternate)",
}


def scan_bus(bus_num: int) -> list[int]:
    import smbus2

    found = []
    bus = smbus2.SMBus(bus_num)
    try:
        for addr in range(0x03, 0x78):
            try:
                bus.read_byte(addr)
                found.append(addr)
            except OSError:
                pass
    finally:
        bus.close()
    return found


def main():
    print("=== I2C diagnostic ===")
    print(f"config: I2C_CAN_CH={Config.I2C_CAN_CH}, addr=0x{Config.I2C_CAN_ADDR:02X}")
    print(f"config: LCD_I2C_CH={Config.LCD_I2C_CH}")
    print()

    dev_nodes = sorted(glob.glob("/dev/i2c-*"))
    if not dev_nodes:
        print("ERROR: /dev/i2c-* not found. Enable I2C:")
        print("  sudo raspi-config -> Interface Options -> I2C -> Enable")
        print("  then reboot")
        return 1

    print("I2C device nodes:")
    for node in dev_nodes:
        print(f"  {node}")
    print()

    any_found = False
    for node in dev_nodes:
        bus_num = int(node.rsplit("-", 1)[-1])
        print(f"--- scan bus {bus_num} ({node}) ---")
        try:
            addrs = scan_bus(bus_num)
        except OSError as err:
            print(f"  open/scan failed: {err}")
            continue

        if not addrs:
            print("  (no device responded)")
        else:
            any_found = True
            for addr in addrs:
                name = KNOWN_DEVICES.get(addr, "unknown")
                mark = " <-- CAN module" if addr == Config.I2C_CAN_ADDR else ""
                print(f"  0x{addr:02X}  {name}{mark}")

    print()
    if not any_found:
        print("No I2C devices found on any bus.")
        print()
        print("Hardware checklist (Pi Zero 2 W, Seeed I2C-CAN 0x25):")
        print("  Pin 1 (3.3V) -> VCC on module")
        print("  Pin 3 (SDA, GPIO2) -> SDA (Yellow on Grove/HY)")
        print("  Pin 5 (SCL, GPIO3) -> SCL (White)")
        print("  Pin 6 (GND) -> GND (Black)")
        print("  Do NOT swap SDA/SCL")
        print("  Power off Pi and module, wait 10s, reconnect, boot, scan again")
        print("  Module RX/TX LED: constant blink = CAN init failed (check CAN wiring/baud)")
        print()
        print("Also try:")
        print("  sudo i2cdetect -y 0")
        print("  sudo i2cdetect -y 1")
        print("  dmesg | tail -30 | grep -i i2c")
        return 1

    can_bus = None
    for node in dev_nodes:
        bus_num = int(node.rsplit("-", 1)[-1])
        try:
            if Config.I2C_CAN_ADDR in scan_bus(bus_num):
                can_bus = bus_num
                break
        except OSError:
            pass

    if can_bus is None:
        print(f"WARNING: CAN module 0x{Config.I2C_CAN_ADDR:02X} not found.")
        print(f"  config I2C_CAN_CH={Config.I2C_CAN_CH} may be wrong.")
    elif can_bus != Config.I2C_CAN_CH:
        print(f"NOTE: CAN found on bus {can_bus}, but config I2C_CAN_CH={Config.I2C_CAN_CH}")
        print(f"  -> set Config.I2C_CAN_CH = {can_bus} in config.py")
    else:
        print(f"OK: CAN module found on bus {can_bus} (matches config).")

    if Config.LCD_I2C_CH != Config.I2C_CAN_CH:
        print()
        print(f"NOTE: LCD uses bus {Config.LCD_I2C_CH}, CAN uses bus {Config.I2C_CAN_CH}.")
        print("  If both modules share the same SDA/SCL wires, use the same bus number.")

    return 0


if __name__ == "__main__":
    sys.exit(main())

"""Standalone I2C-CAN receive test for Raspberry Pi."""

import os
import time

from config import Config
from lib.i2c_can import I2C_CAN

if __name__ == "__main__":
    os.environ.setdefault("I2C_CAN_DEBUG", "1")

    i2c_can = I2C_CAN(Config.I2C_CAN_CH, Config.I2C_CAN_ADDR, is_silent=False)
    i2c_can.begin(Config.I2C_CAN_BAUD)

    if Config.I2C_CAN_FILTER_MODE == "obd":
        i2c_can.init_obd_filters()
    elif Config.I2C_CAN_FILTER_MODE == "all":
        i2c_can.init_accept_all_filters()

    print(
        f"I2C-CAN listen: ch={Config.I2C_CAN_CH}, addr=0x{Config.I2C_CAN_ADDR:02X}, "
        f"baud={Config.I2C_CAN_BAUD}, filter={Config.I2C_CAN_FILTER_MODE}"
    )
    print("Send CAN frames from USB-CAN adapter (500kbps). Ctrl-C to stop.")

    try:
        while True:
            size = i2c_can.check_receive()
            if size <= 0:
                time.sleep(0.01)
                continue
            print(f"DNUM={size}")
            while size > 0:
                msg = i2c_can.read_can()
                if msg is not None and msg.is_valid_can_msg():
                    print(f"RX CAN [{msg.id:03X}] {msg.data_to_hex_str()}")
                else:
                    print(f"RX invalid frame: raw={i2c_can.last_recv_raw}")
                size = i2c_can.check_receive()
            time.sleep(0.01)
    except KeyboardInterrupt:
        pass

    print("exit")

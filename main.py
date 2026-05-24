
import RPi.GPIO as GPIO
import time
import os

from config import Config

# use RotaryEncoderaWithPushSwitchRGBLED
from switch import RotaryEncoderaWithPushSwitchRGBLED
# use LCD
from lib.lcd1602 import LCD1602
from lib.i2c_can import I2C_CAN

is_use_rotary_encoder = True
is_use_i2c_can = True
is_use_lcd = True
is_use_usb_storage = False


def init_i2c_can():
    """Initialize I2C-CAN module with retry."""
    last_err = None
    for attempt in range(1, Config.I2C_INIT_RETRY_COUNT + 1):
        try:
            i2c_can = I2C_CAN(Config.I2C_CAN_CH, Config.I2C_CAN_ADDR)
            i2c_can.begin(Config.I2C_CAN_BAUD)
            time.sleep(0.05)
            print(
                f"I2C-CAN initialized: ch={Config.I2C_CAN_CH}, addr=0x{Config.I2C_CAN_ADDR:02X}, baud={Config.I2C_CAN_BAUD}"
            )
            return i2c_can
        except OSError as err:
            last_err = err
            print(
                f"I2C init failed ({attempt}/{Config.I2C_INIT_RETRY_COUNT}): {err}. "
                f"retry in {Config.I2C_INIT_RETRY_WAIT_SEC:.1f}s"
            )
            time.sleep(Config.I2C_INIT_RETRY_WAIT_SEC)
    raise last_err

class RotaryEncoderaWithPushSwitchRGBLED_1 (RotaryEncoderaWithPushSwitchRGBLED):
    def __init__(self, is_silent=True):
        super().__init__(
            Config.pin_id_rot_1_a,
            Config.pin_id_rot_1_b,
            Config.pin_id_rot_1_push_sw,
            Config.pin_id_led_1_r,
            Config.pin_id_led_1_g,
            Config.pin_id_led_1_b,
            self.event_rot_sw_cw,
            self.event_rot_sw_ccw,
            self.event_rot_sw_pushed
        )
        self.is_silent = is_silent

    def event_rot_sw_cw(self):
        if not self.is_silent: print(Config.text_rot_1_cw)
        print(Config.text_rot_1_cw)
        pass

    def event_rot_sw_ccw(self):
        if not self.is_silent: print(Config.text_rot_1_ccw)
        print(Config.text_rot_1_ccw)
        pass

    def event_rot_sw_pushed(self):
        e_state = super().get_state()
        print(f"RotaryEncoderaWithPushSwitchRGBLED_1: event_rot_sw_pushed: {e_state}")
        if RotaryEncoderaWithPushSwitchRGBLED.State.OFF == e_state:
            print(Config.text_rot_1_state_off)
            if not self.is_silent: print(Config.text_rot_1_state_off)
        elif RotaryEncoderaWithPushSwitchRGBLED.State.ON_R == e_state:
            print(Config.text_rot_1_state_a)
            if not self.is_silent: print(Config.text_rot_1_state_a)
        elif RotaryEncoderaWithPushSwitchRGBLED.State.ON_G == e_state:
            print(Config.text_rot_1_state_b)
            if not self.is_silent: print(Config.text_rot_1_state_b)
        elif RotaryEncoderaWithPushSwitchRGBLED.State.ON_RG == e_state:
            print(Config.text_rot_1_state_ab)
            if not self.is_silent: print(Config.text_rot_1_state_ab)
        pass

class RotaryEncoderaWithPushSwitchRGBLED_2 (RotaryEncoderaWithPushSwitchRGBLED):
    def __init__(self, is_silent=True):
        super().__init__(
            Config.pin_id_rot_2_a,
            Config.pin_id_rot_2_b,
            Config.pin_id_rot_2_push_sw,
            Config.pin_id_led_2_r,
            Config.pin_id_led_2_g,
            Config.pin_id_led_2_b,
            self.event_rot_sw_cw,
            self.event_rot_sw_ccw,
            self.event_rot_sw_pushed
        )
        self.is_silent = is_silent

    def event_rot_sw_cw(self):
        if not self.is_silent: print(Config.text_rot_2_cw)
        print(Config.text_rot_2_cw)
        pass

    def event_rot_sw_ccw(self):
        if not self.is_silent: print(Config.text_rot_2_ccw)
        print(Config.text_rot_2_ccw)
        pass

    def event_rot_sw_pushed(self):
        e_state = super().get_state()
        print(f"RotaryEncoderaWithPushSwitchRGBLED_2: event_rot_sw_pushed: {e_state}")
        if RotaryEncoderaWithPushSwitchRGBLED.State.OFF == e_state:
            print(Config.text_rot_2_state_off)
            if not self.is_silent: print(Config.text_rot_2_state_off)
        elif RotaryEncoderaWithPushSwitchRGBLED.State.ON_R == e_state:
            print(Config.text_rot_2_state_a)
            if not self.is_silent: print(Config.text_rot_2_state_a)
        elif RotaryEncoderaWithPushSwitchRGBLED.State.ON_G == e_state:
            print(Config.text_rot_2_state_b)
            if not self.is_silent: print(Config.text_rot_2_state_b)
        elif RotaryEncoderaWithPushSwitchRGBLED.State.ON_RG == e_state:
            print(Config.text_rot_2_state_ab)
            if not self.is_silent: print(Config.text_rot_2_state_ab)
        pass



def serial_received(msg : str):
    global rot_sw1, rot_sw2
    print(msg)
    if(msg == "AUTOPILOT VS SLOT INDEX:1\r\n"):
        rot_sw1.set_state(RotaryEncoderaWithPushSwitchRGBLED.State.ON_R)   # unmanaged
    elif(msg == "AUTOPILOT VS SLOT INDEX:2\r\n"):
        rot_sw1.set_state(RotaryEncoderaWithPushSwitchRGBLED.State.ON_G)   # managed
    elif(msg == "AUTOPILOT ALTITUDE SLOT INDEX:1\r\n"):
        rot_sw2.set_state(RotaryEncoderaWithPushSwitchRGBLED.State.ON_R)   # unmanaged
    elif(msg == "AUTOPILOT ALTITUDE SLOT INDEX:2\r\n"):
        rot_sw2.set_state(RotaryEncoderaWithPushSwitchRGBLED.State.ON_G)   # managed

def main():
    global rot_sw1, rot_sw2
    global logfile
    global is_use_i2c_can
    
    if is_use_usb_storage:
        # path_to_usb にログを書き込む
        logfile = open(Config.path_to_usb + "/log.txt", "a")
        logfile.write("--------------------------------\n")
    else:
        logfile = None
    
    if is_use_rotary_encoder:
    # serial = MySerial(serial_received).start()
        rot_sw1 = RotaryEncoderaWithPushSwitchRGBLED_1(is_silent=False)
        rot_sw2 = RotaryEncoderaWithPushSwitchRGBLED_2(is_silent=False)
    
    if is_use_lcd:
        lcd_i2c_ch = 0
        lcd = LCD1602(lcd_i2c_ch)
    
    if is_use_i2c_can:
        try:
            i2c_can = init_i2c_can()
        except OSError as err:
            print("I2C-CAN module initialization failed.")
            print(f"Last error: {err}")
            print("Check:")
            print("- I2C is enabled: sudo raspi-config -> Interface Options -> I2C")
            print("- Wiring (SDA/SCL/GND/3.3V) and pull-up resistors")
            print("- Device address: run 'i2cdetect -y 1' and confirm 0x25")
            print("- I2C bus number (some boards use bus 0)")
            is_use_i2c_can = False
        
        
    
    if is_use_rotary_encoder:
    # test
        rot_sw1.set_state(RotaryEncoderaWithPushSwitchRGBLED.State.ON_R)
        rot_sw2.set_state(RotaryEncoderaWithPushSwitchRGBLED.State.ON_R)
        time.sleep(0.5)
        rot_sw1.set_state(RotaryEncoderaWithPushSwitchRGBLED.State.ON_G)
        rot_sw2.set_state(RotaryEncoderaWithPushSwitchRGBLED.State.ON_G)
        time.sleep(0.5)
        rot_sw1.set_state(RotaryEncoderaWithPushSwitchRGBLED.State.ON_B)
        rot_sw2.set_state(RotaryEncoderaWithPushSwitchRGBLED.State.ON_B)
        time.sleep(0.5)
        rot_sw1.set_state(RotaryEncoderaWithPushSwitchRGBLED.State.ON_RGB)
        rot_sw2.set_state(RotaryEncoderaWithPushSwitchRGBLED.State.ON_RGB)
        time.sleep(0.5)    
        rot_sw1.set_state(RotaryEncoderaWithPushSwitchRGBLED.State.ON_RGB)
        rot_sw2.set_state(RotaryEncoderaWithPushSwitchRGBLED.State.ON_RGB)
        time.sleep(2.0)
    
        rot_sw1.set_state(RotaryEncoderaWithPushSwitchRGBLED.State.OFF)
        rot_sw2.set_state(RotaryEncoderaWithPushSwitchRGBLED.State.OFF)
        time.sleep(0.5)
    
    
    cnt = 0
    i2c_error_count = 0
    try:
        data = None
        print("please input Ctrl-C and wait few seconds to terminalte this program.")
        while True:
            if is_use_i2c_can:
                try:
                    size = i2c_can.check_receive()  # Read the size of stored frames
                    # print("Stored frame size:", size)
                    if size > 0:
                        data = i2c_can.read_can()  # Read CAN messages
                        if is_use_usb_storage:
                            logfile.write(f"CAN [{data.id:03X}] {data.data_to_hex_str()}\n")
                        print(f"CAN [{data.id:03X}] {data.data_to_hex_str()}")
                    else:
                        data = None
                    i2c_error_count = 0
                except OSError as err:
                    # Keep running even when the I2C device temporarily does not respond.
                    i2c_error_count += 1
                    data = None
                    if i2c_error_count == 1 or i2c_error_count % 10 == 0:
                        print(f"I2C read failed ({i2c_error_count}): {err}")
            
            if is_use_rotary_encoder:
                val1 = GPIO.input(Config.pin_id_rot_1_push_sw)  # keep GPIO event detection
                val2 = GPIO.input(Config.pin_id_rot_2_push_sw)  # keep GPIO event detection
            
            if is_use_lcd:
                lcd.home()
                if data:
                    lcd.home()
                    lcd.print(f"CAN [{data.id:03X}] {data.data_to_hex_str()}")
                    if is_use_rotary_encoder:
                        rot_sw1.set_state(RotaryEncoderaWithPushSwitchRGBLED.State.ON_G)
                        rot_sw2.set_state(RotaryEncoderaWithPushSwitchRGBLED.State.ON_G)
                else:
                    lcd.home()
                    lcd.print("CAN id:None MSG: None")
                    if is_use_rotary_encoder:
                        rot_sw1.set_state(RotaryEncoderaWithPushSwitchRGBLED.State.OFF)
                        rot_sw2.set_state(RotaryEncoderaWithPushSwitchRGBLED.State.OFF)
                
                lcd.setCursor(0, 1)
                if is_use_rotary_encoder:
                    lcd.print(f"[{cnt}]sw:{val1},{val2}")
        
                # print(f"[{cnt}]rot_push_sw: {val1}, {val2}")
                cnt += 1
                time.sleep(1)
    except KeyboardInterrupt:
        pass
    
    finally:
        if is_use_usb_storage:
            logfile.close()
            logfile = None
        
        if is_use_lcd:
            lcd.close()
        if is_use_i2c_can:
            # i2c_can.close()
            pass
        if is_use_rotary_encoder:
            pass
            # rot_sw1.close()
            # rot_sw2.close()
        # serial.end()
    print('exit')

if __name__ == "__main__":
    main()

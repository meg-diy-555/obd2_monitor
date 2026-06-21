
import RPi.GPIO as GPIO
import time
import os
import threading

from config import Config

# use RotaryEncoderaWithPushSwitchRGBLED
from switch import RotaryEncoderaWithPushSwitchRGBLED, gpio_lock, RotaryEncoder
# use LCD
from lib.lcd1602 import LCD1602
from lib.i2c_can import I2C_CAN, CAN_MSG

is_silent = False
is_use_rotary_encoder = True
is_use_i2c_can = True
is_use_lcd = True
is_use_usb_storage = True

prev_psw_valid = 0
val_psw2_valid = 0
dir_rot_valid = 0
dir_rot2_valid = 0
data = None
prev_valid_data = None


class InputData:
    rot_sw1 = RotaryEncoder.RotaryEncoderData()
    rot_sw2 = RotaryEncoder.RotaryEncoderData()

class RotaryEncoderWithPushSwitchRGBLED_1 (RotaryEncoderaWithPushSwitchRGBLED):
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
        pass

    def event_rot_sw_ccw(self):
        if not self.is_silent: print(Config.text_rot_1_ccw)
        pass

    def event_rot_sw_pushed(self):
        e_state = super().get_led_state()
        # print(f"RotaryEncoderaWithPushSwitchRGBLED_1: event_rot_sw_pushed: {e_state}")
        if RotaryEncoderaWithPushSwitchRGBLED.LED_State.OFF == e_state:
            if not self.is_silent: print(Config.text_rot_1_state_off)
        elif RotaryEncoderaWithPushSwitchRGBLED.LED_State.ON_R == e_state:
            if not self.is_silent: print(Config.text_rot_1_state_a)
        elif RotaryEncoderaWithPushSwitchRGBLED.LED_State.ON_G == e_state:
            if not self.is_silent: print(Config.text_rot_1_state_b)
        elif RotaryEncoderaWithPushSwitchRGBLED.LED_State.ON_RG == e_state:
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
        pass

    def event_rot_sw_ccw(self):
        if not self.is_silent: print(Config.text_rot_2_ccw)
        pass

    def event_rot_sw_pushed(self):
        e_state = super().get_led_state()
        # print(f"RotaryEncoderaWithPushSwitchRGBLED_2: event_rot_sw_pushed: {e_state}")
        if RotaryEncoderaWithPushSwitchRGBLED.LED_State.OFF == e_state:
            if not self.is_silent: print(Config.text_rot_2_state_off)
        elif RotaryEncoderaWithPushSwitchRGBLED.LED_State.ON_R == e_state:
            if not self.is_silent: print(Config.text_rot_2_state_a)
        elif RotaryEncoderaWithPushSwitchRGBLED.LED_State.ON_G == e_state:
            if not self.is_silent: print(Config.text_rot_2_state_b)
        elif RotaryEncoderaWithPushSwitchRGBLED.LED_State.ON_RG == e_state:
            if not self.is_silent: print(Config.text_rot_2_state_ab)
        pass

def event_can_received(msg: CAN_MSG):
    global prev_valid_data
    if not is_silent:
        print(f"CAN [{msg.id:03X}] {msg.data_to_hex_str()}")


def lcd_display_thread(lcd, thread_sleep_sec=0.1):
    global prev_psw_valid, val_psw2_valid, dir_rot_valid, dir_rot2_valid
    global prev_valid_data
    cnt = 0
    try:
        while True:
            try:
                lcd.home()
                if prev_valid_data:
                    lcd.print(f"CAN [{prev_valid_data.id:03X}] {prev_valid_data.data_to_hex_str()}")
                else:   
                    lcd.print("CAN [---] ------")
                lcd.setCursor(0, 1)
                if is_use_rotary_encoder:
                    lcd.print(f"[{cnt}]sw:{prev_psw_valid},{val_psw2_valid},[{dir_rot_valid}],[{dir_rot2_valid}]")
                cnt = (cnt + 1) if cnt < 9 else 0
            except Exception as err:
                print(f"lcd_display_thread error: {err}")
            time.sleep(0.1)
    except KeyboardInterrupt:
        pass


def print_i2c_can_init_error(err):
    if not is_silent:
        print("I2C-CAN module initialization failed.")
        print(f"Last error: {err}")
        print("Check:")
        print("- I2C is enabled: sudo raspi-config -> Interface Options -> I2C")
        print("- Wiring (SDA/SCL/GND/3.3V) and pull-up resistors")
        print("- Device address: run 'i2cdetect -y 1' and confirm 0x25")
        print("- I2C bus number (some boards use bus 0)")


def rot_led_init_test():
    rot_sw1.set_led_state(RotaryEncoderaWithPushSwitchRGBLED.LED_State.ON_RGB)
    rot_sw2.set_led_state(RotaryEncoderaWithPushSwitchRGBLED.LED_State.ON_RGB)
    time.sleep(0.5)
    rot_sw1.set_led_state(RotaryEncoderaWithPushSwitchRGBLED.LED_State.OFF)
    rot_sw2.set_led_state(RotaryEncoderaWithPushSwitchRGBLED.LED_State.OFF)
    time.sleep(0.5)

    
def main():
    global rot_sw1, rot_sw2
    global logfile, lcd, i2c_can
    global is_use_i2c_can
    
    if is_use_usb_storage:
        # path_to_usb にログを書き込む
        logfile = open(Config.path_to_usb + "/log.txt", "a")
        logfile.write("--------------------------------\n")
    else:
        logfile = None
    
    if is_use_lcd:
        lcd = LCD1602(Config.LCD_I2C_CH)
    
    if is_use_i2c_can:
        try:
            i2c_can = I2C_CAN(
                Config.I2C_CAN_CH,
                Config.I2C_CAN_ADDR,
                event_can_received,
                is_silent,
            )
            i2c_can.begin(Config.I2C_CAN_BAUD)
            if Config.I2C_CAN_FILTER_MODE == "obd":
                i2c_can.init_obd_filters()
            elif Config.I2C_CAN_FILTER_MODE == "all":
                i2c_can.init_accept_all_filters()
            time.sleep(0.05)
            if not is_silent:
                print(f"I2C-CAN ready: ch={Config.I2C_CAN_CH}, addr=0x{Config.I2C_CAN_ADDR:02X}, filter={Config.I2C_CAN_FILTER_MODE}")
        except OSError as err:
            print_i2c_can_init_error(err)
            is_use_i2c_can = False

    if is_use_rotary_encoder:
    # serial = MySerial(serial_received).start()
        rot_sw1 = RotaryEncoderWithPushSwitchRGBLED_1(is_silent=False)
        rot_sw2 = RotaryEncoderaWithPushSwitchRGBLED_2(is_silent=False)
        rot_led_init_test()
    
    try:
        if not is_silent: print("please input Ctrl-C and wait few seconds to terminalte this program.")
        
        
        # create thread for rotary encoders (daemon: run in background, do not join)
        if is_use_rotary_encoder:
            thread_rotary_encoder1 = threading.Thread(
                target=rot_sw1.rotaryencoder.chech_rotary_encoder_changed_thread,
                args=(InputData.rot_sw1, Config.pin_id_rot_1_a, Config.pin_id_rot_1_b),
                daemon=True,
                name="rotary_encoder_1",
            )
            thread_rotary_encoder1.start()
            thread_rotary_encoder2 = threading.Thread(
                target=rot_sw2.rotaryencoder.chech_rotary_encoder_changed_thread,
                args=(InputData.rot_sw2, Config.pin_id_rot_2_a, Config.pin_id_rot_2_b),
                daemon=True,
                name="rotary_encoder_2",
            )
            thread_rotary_encoder2.start()
            thread_push_switch1 = threading.Thread(
                target=rot_sw1.pushswitch.chech_push_switch_changed_thread,
                args=(InputData.rot_sw1, Config.pin_id_rot_1_push_sw, 0.1),
                daemon=True,
                name="push_switch_1",
            )
            thread_push_switch1.start()
            thread_push_switch2 = threading.Thread(
                target=rot_sw2.pushswitch.chech_push_switch_changed_thread,
                args=(InputData.rot_sw2, Config.pin_id_rot_2_push_sw, 0.1),
                daemon=True,
                name="push_switch_2",
            )
            thread_push_switch2.start()
        
        # create thread for I2C-CAN
        if is_use_i2c_can:
            thread_i2c_can = threading.Thread(
                target=i2c_can.check_i2c_can_thread,
                args=(),
                daemon=True,
                name="i2c_can",
            )
            thread_i2c_can.start()
            
        if is_use_lcd:
            thread_lcd = threading.Thread(
                target=lcd_display_thread,
                args=(lcd, 1),
                daemon=True,
                name="lcd",
            )
            thread_lcd.start()
        
        while True:
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
    if not is_silent: print('exit')

if __name__ == "__main__":
    main()

from lib.i2c_can import I2C_CAN

class Config:

    pin_id_rot_1_a = 17
    pin_id_rot_1_b = 4
    pin_id_rot_1_push_sw = 22
    pin_id_led_1_r = 9
    pin_id_led_1_g = 10
    pin_id_led_1_b = 27
    text_rot_1_cw = "ROT1_CW"
    text_rot_1_ccw = "ROT1_CCW"
    text_rot_1_state_off = "ROT1_ON"
    text_rot_1_state_a = "ROT1_A"
    text_rot_1_state_b = "ROT1_B"
    text_rot_1_state_ab = "ROT1_AB"

    pin_id_rot_2_a = 6
    pin_id_rot_2_b = 13
    pin_id_rot_2_push_sw = 5
    pin_id_led_2_r = 26
    pin_id_led_2_g = 16
    pin_id_led_2_b = 11
    text_rot_2_cw = "ROT2_CW"
    text_rot_2_ccw = "ROT2_CCW"
    text_rot_2_state_off = "ROT2_ON"
    text_rot_2_state_a = "ROT2_A"
    text_rot_2_state_b = "ROT2_B"
    text_rot_2_state_ab = "ROT2_AB"

    path_to_usb = "/home/meg/usb"
    
    I2C_CAN_CH = 1
    I2C_CAN_ADDR = 0x25
    I2C_CAN_BAUD = I2C_CAN.I2C_CAN_BAUD.CAN_500KBPS.value
    I2C_CAN_FILTER_MODE = "none"  # "none": Arduino同様デフォルト / "all": 全ID / "obd": 0x7E8のみ
    I2C_INIT_RETRY_COUNT = 5
    I2C_INIT_RETRY_WAIT_SEC = 0.5

    LCD_I2C_CH = 0

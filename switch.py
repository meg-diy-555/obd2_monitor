import RPi.GPIO as GPIO
from enum import IntEnum
import time
import threading
from gpiozero import LED
from enum import Enum

gpio_lock = threading.Lock()

class Switch:
    def __init__(self):
        pass


    class SwitchState(Enum):
        OFF = 0
        ON = 1
        
    class SwitchData:
        def __init__(self):
            self.val_psw = Switch.SwitchState.OFF

class RotaryEncoder(Switch):
    
    class RotaryEncoderDirection(Enum):
        CW = 1
        CCW = -1
        NONE = 0
        
    class RotaryEncoderData:
        def __init__(self):
            self.dir_rot = RotaryEncoder.RotaryEncoderDirection.NONE
            self.prev_dir_rot_valid = RotaryEncoder.RotaryEncoderDirection.NONE
        
    def __init__(self, pin_id_rot_a: int, pin_id_rot_b: int, event_rot_sw_cw, event_rot_sw_ccw, is_silent=True):
        self.pin_id_rot_a = pin_id_rot_a
        self.pin_id_rot_b = pin_id_rot_b
        self.event_rot_sw_cw = event_rot_sw_cw
        self.event_rot_sw_ccw = event_rot_sw_ccw
        self.is_silent = is_silent
        # initialize GPIO pins
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(pin_id_rot_a, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        # bouncetime は省略（None = デバウンスなし）。0 は rpi-lgpio で ValueError になる
        # GPIO.add_event_detect(pin_id_rot_a, GPIO.FALLING,
        #                       callback=self._event_callback_rot_sw_falling)
        GPIO.setup(pin_id_rot_b, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        # GPIO.add_event_detect(pin_id_rot_b, GPIO.FALLING,
        #                       callback=self._event_callback_rot_sw_falling)

    def __delete__(self):
        # release evets and GPIO pins
        pins = [self.pin_id_rot_a, self.pin_id_rot_b]
        GPIO.setmode(GPIO.BCM)
        GPIO.remove_event_detect(pins)
        GPIO.cleanup(pins)

    def chech_rotary_encoder_changed_thread(self, input_data: RotaryEncoderData, pin_id_rot_a: int, pin_id_rot_b: int, is_silent=True) -> None:
        val_rot_a = 0
        val_rot_b = 0
        
        try:
            while True:
                self.dir_rot, val_rot_a, val_rot_b = self.chech_rotary_encoder_changed_thread_process(pin_id_rot_a, pin_id_rot_b, val_rot_a, val_rot_b, is_silent)
                input_data.dir_rot = self.dir_rot
        
                if self.dir_rot != RotaryEncoder.RotaryEncoderDirection.NONE:
                    self.prev_dir_rot_valid = self.dir_rot
                # time.sleep(0.01)
        except KeyboardInterrupt:
            pass


    def chech_rotary_encoder_changed_thread_process(self, pin_id_rot_a: int, pin_id_rot_b: int, val_rot_a_prev: int, val_rot_b_prev: int, is_silent=True) -> RotaryEncoderDirection:
        dir_rot = RotaryEncoder.RotaryEncoderDirection.NONE
        with gpio_lock:
            val_rot_a = GPIO.input(pin_id_rot_a)
            val_rot_b = GPIO.input(pin_id_rot_b)

        dir_rot = self.calc_rotary_encoder_direction(
            val_rot_a, val_rot_b, val_rot_a_prev, val_rot_b_prev)
        if RotaryEncoder.RotaryEncoderDirection.CW == dir_rot:
            self.event_rot_sw_cw()
        elif RotaryEncoder.RotaryEncoderDirection.CCW == dir_rot:
            self.event_rot_sw_ccw()

        return dir_rot, val_rot_a, val_rot_b
    
            
    def calc_rotary_encoder_direction(self, val_rot_a: int, val_rot_b: int, val_rot_a_prev: int, val_rot_b_prev: int) -> RotaryEncoderDirection:
        dir_rot = RotaryEncoder.RotaryEncoderDirection.NONE
        if (val_rot_a != val_rot_a_prev) or (val_rot_b != val_rot_b_prev):
            is_rot1_a_falling = ((val_rot_a_prev == 1) and (val_rot_a == 0))
            is_rot1_b_falling = ((val_rot_b_prev == 1) and (val_rot_b == 0))
            # check if direction is clockwise or counterclockwise
            if is_rot1_a_falling and (val_rot_b == 1):
                dir_rot = RotaryEncoder.RotaryEncoderDirection.CW
                # rot_sw1.event_rot_sw_cw()
            elif is_rot1_b_falling and (val_rot_a == 1):
                dir_rot = RotaryEncoder.RotaryEncoderDirection.CCW
                # rot_sw1.event_rot_sw_ccw()
        return dir_rot
    

class PushSwitch(Switch):
    def __init__(self, pin_id_sw: int, event_sw_pushed, bouncetime=100, pull_up_down=GPIO.PUD_UP, edge=GPIO.FALLING):
        # initialize GPIO pins
        self.pin_id_rot_sw = pin_id_sw
        self.event_sw_pushed = event_sw_pushed
        self.val_psw =  Switch.SwitchState.OFF
        self.prev_psw_valid = Switch.SwitchState.OFF
        
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(pin_id_sw, GPIO.IN, pull_up_down=pull_up_down)
        GPIO.add_event_detect(pin_id_sw, edge,
                              callback=self._event_callback_pushsw, bouncetime=bouncetime)

    def _event_callback_pushsw(self, gpio_pin):
        if self.pin_id_rot_sw == gpio_pin:
            with gpio_lock:
                is_pushed = (0 == GPIO.input(self.pin_id_rot_sw))
            if not is_pushed:
                # print("rot sw pushed. pin: " , str(self.pin_id_rot_sw))
                self.event_sw_pushed()

    def __delete__(self):
        # release evets and GPIO pins
        GPIO.setmode(GPIO.BCM)
        GPIO.remove_event_detect(self.pin_id_sw)
        GPIO.cleanup(self.pin_id_sw)

    def chech_push_switch_changed_thread(self, input_data: Switch.SwitchData, pin_id_sw: int):
        try:
            while True:
                val_psw = input_data.val_psw = self.chech_push_switch_changed_thread_process(pin_id_sw, val_psw)
                if val_psw != Switch.SwitchState.OFF:
                    self.prev_psw_valid = val_psw
                time.sleep(0.01)
        except KeyboardInterrupt:
            pass


    def chech_push_switch_changed_thread_process(self, pin_id_sw: int, prev_swith_state: Switch.SwitchState) -> Switch.SwitchState:
        with gpio_lock:
            val_psw = GPIO.input(pin_id_sw)  # keep GPIO event detection
        switch_state = Switch.SwitchState.ON if val_psw == 0 else Switch.SwitchState.OFF
        if Switch.SwitchState.ON == switch_state and prev_swith_state == Switch.SwitchState.OFF:
            self.event_sw_pushed()
        return switch_state
        
        
class PushSwitchWithLED(PushSwitch):
    class State (IntEnum):
        OFF = 1
        ON = 2

    def __init__(self, pin_id_sw: int, pin_id_led: int, event_sw_pushed,  bouncetime=100, active_high=True, pull_up_down=GPIO.PUD_UP):
        super().__init__(pin_id_sw, event_sw_pushed, bouncetime, pull_up_down)
        self.e_state = self.State.OFF
        self.event_sw_pushed = event_sw_pushed
        self.led = LED(pin_id_led, initial_value=False, active_high=active_high)

    def set_state(self, e_state: State):
        if self.e_state is not e_state:
            self.e_state = e_state
            if e_state == self.State.ON:
                self.led.on()
            else:
                self.led.off()

    def __delete__(self):
        super().__delete__()
        GPIO.setmode(GPIO.BCM)
        GPIO.cleanup(self.pin_id_sw)


class RotaryEncoderaWithPushSwitch(Switch): 
    def __init__(self, pin_id_rot_a: int, pin_id_rot_b: int, pin_id_rot_sw: int, event_rot_sw_cw, event_rot_sw_ccw, event_rot_sw_pushed, pull_up_down=GPIO.PUD_UP, edge=GPIO.FALLING):
        self.rotaryencoder = RotaryEncoder(
            pin_id_rot_a, pin_id_rot_b, event_rot_sw_cw, event_rot_sw_ccw)
        self.pushswitch = PushSwitch(
            pin_id_rot_sw, event_rot_sw_pushed, pull_up_down=pull_up_down, edge=edge)
        
    class RotaryEncoderWithPushSwitchData(RotaryEncoder.RotaryEncoderData, Switch.SwitchData):
        def __init__(self):
            self.dir_rot = RotaryEncoder.RotaryEncoderDirection.NONE
            self.val_psw = Switch.SwitchState.OFF
        
    def check_rotary_encoder_with_push_switch_changed_thread(self, input_data: RotaryEncoderWithPushSwitchData, pin_id_rot_a: int, pin_id_rot_b: int, pin_id_sw: int, is_silent=True):
        global dir_rot, val_psw
        global prev_dir_rot_valid, prev_psw_valid
        val_rot_a = 0
        val_rot_b = 0
        dir_rot = prev_dir_rot_valid = RotaryEncoder.RotaryEncoderDirection.NONE
        val_psw = prev_psw_valid = Switch.SwitchState.OFF
        try:
            while True:
                dir_rot, val_rot_a, val_rot_b = self.rotaryencoder.chech_rotary_encoder_changed_thread_process(
                    pin_id_rot_a, pin_id_rot_b, val_rot_a, val_rot_b, is_silent)
                input_data.dir_rot = dir_rot
                if dir_rot != RotaryEncoder.RotaryEncoderDirection.NONE:
                    prev_dir_rot_valid = dir_rot

                input_data.val_psw = val_psw = self.pushswitch.chech_push_switch_changed_thread_process(
                    pin_id_sw, val_psw)
                if val_psw != Switch.SwitchState.OFF:
                    prev_psw_valid = val_psw
        except KeyboardInterrupt:
            pass
    
    
class RotaryEncoderaWithPushSwitch2CLED(RotaryEncoderaWithPushSwitch):
    class LED_State (IntEnum):
        OFF = 1
        ON_A = 2
        ON_B = 3
        ON_AB = 4

    def __init__(self, pin_id_rot_a: int, pin_id_rot_b: int, pin_id_rot_sw: int, pin_id_led_1: int, pin_id_led_2: int,
                 event_rot_sw_cw, event_rot_sw_ccw, event_rot_sw_pushed, active_high=True, pull_up_down=GPIO.PUD_UP
                 ):
        super().__init__(pin_id_rot_a, pin_id_rot_b, pin_id_rot_sw, event_rot_sw_cw, event_rot_sw_ccw, event_rot_sw_pushed)
        self.e_led_state = self.LED_State.OFF
        self.pin_id_led_1 = pin_id_led_1
        self.pin_id_led_2 = pin_id_led_2
        self.led_a = LED(pin_id_led_1, active_high=active_high)
        self.led_b = LED(pin_id_led_2, active_high=active_high)
        self.led_a.off()
        self.led_b.off()

    def __delete__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.cleanup([self.pin_id_led_1, self.pin_id_led_2])

    def set_led_state(self, state: LED_State):
        if self.e_led_state != state:
            if self.LED_State.OFF == state:
                self.led_a.off()
                self.led_b.off()
            elif self.LED_State.ON_A == state:
                self.led_a.on()
                self.led_b.off()
            elif self.LED_State.ON_B == state:
                self.led_a.off()
                self.led_b.on()
            elif self.LED_State.ON_AB == state:
                self.led_a.on()
                self.led_b.on()
        self.e_led_state = state

    def get_led_state(self) -> LED_State:
        return self.e_led_state


class RotaryEncoderaWithPushSwitchRGBLED(RotaryEncoderaWithPushSwitch):
    class LED_State (IntEnum):
        OFF = 0b0000
        ON_R = 0b0001
        ON_G = 0b0010
        ON_B = 0b0100
        ON_RG = ON_R | ON_G # 0b0011
        ON_RB = ON_R | ON_G # 0b0101
        ON_GB =  ON_G | ON_B # 0b0110
        ON_RGB =  ON_R | ON_G | ON_B # 0b0111
        

    def __init__(self, pin_id_rot_a: int, pin_id_rot_b: int, pin_id_rot_sw: int, pin_id_led_r: int, pin_id_led_g: int, pin_id_led_b: int,
                 event_rot_sw_cw, event_rot_sw_ccw, event_rot_sw_pushed, led_active_high=False, sw_pull_up_down=GPIO.PUD_DOWN, sw_edge=GPIO.RISING
                 ):
        super().__init__(
            pin_id_rot_a, pin_id_rot_b, pin_id_rot_sw,
            event_rot_sw_cw, event_rot_sw_ccw, event_rot_sw_pushed,
            pull_up_down=sw_pull_up_down, edge=sw_edge)
        self.e_led_state = self.LED_State.OFF
        self.pin_id_led_r = pin_id_led_r
        self.pin_id_led_g = pin_id_led_g
        self.pin_id_led_b = pin_id_led_b
        self.led_r = LED(pin_id_led_r, active_high=led_active_high)
        self.led_g = LED(pin_id_led_g, active_high=led_active_high)
        self.led_b = LED(pin_id_led_b, active_high=led_active_high)
        self.led_r.off()
        self.led_g.off()
        self.led_b.off()

    def __delete__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.cleanup([self.pin_id_led_r, self.pin_id_led_g, self.pin_id_led_b])

    def set_led_state(self, state: LED_State):
        if self.e_led_state != state:
            if state & self.LED_State.ON_R:
                self.led_r.on()
            else:
                self.led_r.off()
            if state & self.LED_State.ON_G:
                self.led_g.on()
            else:
                self.led_g.off()
            if state & self.LED_State.ON_B:
                self.led_b.on()
            else:
                self.led_b.off()
        self.e_led_state = state

    def get_led_state(self) -> LED_State:
        return self.e_led_state

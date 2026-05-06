import RPi.GPIO as GPIO
from enum import IntEnum
import time
from gpiozero import LED

class Switch:
    def __init__(self):
        pass

class RotaryEncoder(Switch):
    def __init__(self, pin_id_rot_a: int, pin_id_rot_b: int, event_rot_sw_cw, event_rot_sw_ccw, is_silent=True):
        self.pin_id_rot_a = pin_id_rot_a
        self.pin_id_rot_b = pin_id_rot_b
        self.event_rot_sw_cw = event_rot_sw_cw
        self.event_rot_sw_ccw = event_rot_sw_ccw
        self.is_silent = is_silent
        # initialize GPIO pins
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(pin_id_rot_a, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(pin_id_rot_a, GPIO.FALLING,
                              callback=self._event_callback_rot_sw_falling, bouncetime=5)
        GPIO.setup(pin_id_rot_b, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(pin_id_rot_b, GPIO.FALLING,
                              callback=self._event_callback_rot_sw_falling, bouncetime=5)

    def __delete__(self):
        # release evets and GPIO pins
        pins = [self.pin_id_rot_a, self.pin_id_rot_b]
        GPIO.setmode(GPIO.BCM)
        GPIO.remove_event_detect(pins)
        GPIO.cleanup(pins)

    def _event_callback_rot_sw_falling(self, gpio_pin):
        # time.sleep(0.001)  # Chattering prevention
        is_on_sw_a = GPIO.input(self.pin_id_rot_a)
        is_on_sw_b = GPIO.input(self.pin_id_rot_b)
        print(f"RotaryEncoder: _event_callback_rot_sw_falling: gpio_pin: {gpio_pin}, is_on_sw_a: {is_on_sw_a}, is_on_sw_b: {is_on_sw_b}")
        if (not is_on_sw_a and not is_on_sw_b):
            pass
        elif (self.pin_id_rot_a == gpio_pin and is_on_sw_a) or (self.pin_id_rot_b == gpio_pin and is_on_sw_b):
            pass
        elif (self.pin_id_rot_a == gpio_pin and is_on_sw_b):
            if not self.is_silent:
                print("[1] gpio_pin:", str(gpio_pin), ", is_on_sw_a:",
                      str(is_on_sw_a), ", is_on_sw_b:", str(is_on_sw_b))
            self.event_rot_sw_cw()
        elif (self.pin_id_rot_b == gpio_pin and not is_on_sw_a):
            if not self.is_silent:
                print("[2] gpio_pin:", str(gpio_pin), ", is_on_sw_a:",
                      str(is_on_sw_a), ", is_on_sw_b:", str(is_on_sw_b))
            self.event_rot_sw_cw()
        elif (self.pin_id_rot_a == gpio_pin and not is_on_sw_b):
            if not self.is_silent:
                print("[3] gpio_pin:", str(gpio_pin), ", is_on_sw_a:",
                      str(is_on_sw_a), ", is_on_sw_b:", str(is_on_sw_b))
            self.event_rot_sw_ccw()
        elif (self.pin_id_rot_b == gpio_pin and is_on_sw_a):
            if not self.is_silent:
                print("[4] gpio_pin:", str(gpio_pin), ", is_on_sw_a:",
                      str(is_on_sw_a), ", is_on_sw_b:", str(is_on_sw_b))
            self.event_rot_sw_ccw()
            
    def hoge():
        pass


class PushSwitch(Switch):
    def __init__(self, pin_id_sw: int, event_sw_pushed, bouncetime=10, pull_up_down=GPIO.PUD_UP, edge=GPIO.FALLING):
        # initialize GPIO pins
        self.pin_id_rot_sw = pin_id_sw
        self.event_sw_pushed = event_sw_pushed
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(pin_id_sw, GPIO.IN, pull_up_down=pull_up_down)
        GPIO.add_event_detect(pin_id_sw, edge,
                              callback=self._event_callback_pushsw, bouncetime=bouncetime)

    def _event_callback_pushsw(self, gpio_pin):
        if self.pin_id_rot_sw == gpio_pin:
            time.sleep(0.01)  # Chattering prevention
            is_pushed = GPIO.input(self.pin_id_rot_sw)
            # if not is_pushed:
                # print("rot sw pushed. pin: " , str(self.pin_id_rot_sw))
            self.event_sw_pushed()

    def __delete__(self):
        # release evets and GPIO pins
        GPIO.setmode(GPIO.BCM)
        GPIO.remove_event_detect(self.pin_id_sw)
        GPIO.cleanup(self.pin_id_sw)


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


class RotaryEncoderaWithPushSwitch2CLED(Switch):
    class State (IntEnum):
        OFF = 1
        ON_A = 2
        ON_B = 3
        ON_AB = 4

    def __init__(self, pin_id_rot_a: int, pin_id_rot_b: int, pin_id_rot_sw: int, pin_id_led_1: int, pin_id_led_2: int,
                 event_rot_sw_cw, event_rot_sw_ccw, event_rot_sw_pushed, active_high=True, pull_up_down=GPIO.PUD_UP
                 ):
        # self.event_rot_sw_cw = event_rot_sw_cw
        # self.event_rot_sw_ccw = event_rot_sw_ccw
        # self.event_rot_sw_pushed = event_rot_sw_pushed
        self.rotaryencoder = RotaryEncoder(
            pin_id_rot_a, pin_id_rot_b, event_rot_sw_cw, event_rot_sw_ccw)
        self.pushswitch = PushSwitch(pin_id_rot_sw, event_rot_sw_pushed, pull_up_down)
        GPIO.setmode(GPIO.BCM)
        self.e_rot_sw_state = self.State.OFF
        self.pin_id_led_1 = pin_id_led_1
        self.pin_id_led_2 = pin_id_led_2
        self.led_a = LED(pin_id_led_1, active_high=active_high)
        self.led_b = LED(pin_id_led_2, active_high=active_high)
        self.led_a.off()
        self.led_b.off()

    def __delete__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.cleanup([self.pin_id_led_1, self.pin_id_led_2])

    def set_state(self, state: State):
        if self.e_rot_sw_state != state:
            if self.State.OFF == state:
                self.led_a.off()
                self.led_b.off()
            elif self.State.ON_A == state:
                self.led_a.on()
                self.led_b.off()
            elif self.State.ON_B == state:
                self.led_a.off()
                self.led_b.on()
            elif self.State.ON_AB == state:
                self.led_a.on()
                self.led_b.on()
        self.e_rot_sw_state = state

    def get_state(self) -> State:
        return self.e_rot_sw_state


class RotaryEncoderaWithPushSwitchRGBLED(Switch):
    class State (IntEnum):
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
        # self.event_rot_sw_cw = event_rot_sw_cw
        # self.event_rot_sw_ccw = event_rot_sw_ccw
        # self.event_rot_sw_pushed = event_rot_sw_pushed
        self.rotaryencoder = RotaryEncoder(
            pin_id_rot_a, pin_id_rot_b, event_rot_sw_cw, event_rot_sw_ccw)
        self.pushswitch = PushSwitch(pin_id_rot_sw, event_rot_sw_pushed, pull_up_down=sw_pull_up_down, edge=sw_edge)
        GPIO.setmode(GPIO.BCM)
        self.e_rot_sw_state = self.State.OFF
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

    def set_state(self, state: State):
        if self.e_rot_sw_state != state:
            if state & self.State.ON_R:
                self.led_r.on()
            else:
                self.led_r.off()
            if state & self.State.ON_G:
                self.led_g.on()
            else:
                self.led_g.off()
            if state & self.State.ON_B:
                self.led_b.on()
            else:
                self.led_b.off()
        self.e_rot_sw_state = state

    def get_state(self) -> State:
        return self.e_rot_sw_state
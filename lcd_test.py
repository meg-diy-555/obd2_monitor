import RPi.GPIO as GPIO
import time
from time import sleep
import smbus2
from lib.lcd1602 import LCD1602

def main():
    
    bus = smbus2.SMBus(0)
    d = LCD1602(bus, 2, 16)
    time.sleep(2.0)
    
    cnt = 0
    try:
        print("please input Ctrl-C and wait few seconds to terminalte this program.")
        while True:
            d.home()
            d.print('TEST')    
            d.setCursor(0, 1)
            d.print(f"[{cnt}]TEST2")
            cnt += 1
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    
    finally:
        bus.close()
    print('exit')

if __name__ == "__main__":
    main()

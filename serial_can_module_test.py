import time
import lib.serial_can_module


def sleep_ms(ms: int) -> None:
    """
    Sleep for a given number of milliseconds.
    
    Parameters
    ----------
    ms : int
        Number of milliseconds to sleep.
    
    Returns
    -------
    None
    """
    time.sleep(ms / 1000.0)

def millis() -> int:
    return (time.time_ns() * 100)


def main():
    print('Initializing...')
    
    counter = 0
    uart_can = lib.serial_can_module.Serial_CAN(0)
    # obd2 = OBD2(uart_can)
    uart_can.begin()
    
    uart_can.change_serial_baudrate(
        lib.serial_can_module.Serial_CAN.SerialBaudRateIndex.SERIAL_RATE_INDEX_38400,
        lib.serial_can_module.Serial_CAN.SerialBaudRateIndex.SERIAL_RATE_INDEX_38400)
    
    uart_can.change_can_rate(lib.serial_can_module.Serial_CAN.CanRateIndex.CAN_RATE_500k)
    
    while True:

        CAN_ID_RESPONSE = 0x7E8
        CAN_ADDR_DATA_BYTES = 0x04
        CAN_CUSTOM_SERVICE = 0x41  # show current data;
        PID_ENGIN_PRM = 0x0C
        # PID_VEHICLE_SPEED = 0x0D
        # PID_COOLANT_TEMP = 0x05
        # rpm = 1500
        CAN_DATA_A = 23
        CAN_DATA_B = 112

        id = CAN_ID_RESPONSE
        dta = [CAN_ADDR_DATA_BYTES, CAN_CUSTOM_SERVICE,
            PID_ENGIN_PRM, CAN_DATA_A, CAN_DATA_B, 0, 0, 0]

        # SEND TEST
        print("sending test pattern [{:d}]: ID[{:x}] {:s}".format(counter, id, str(dta)))
        uart_can.send(id, False, False, 8, dta)   # SEND TO ID:0X55

        # RECEIVE TEST
        # [ret, id, buf] = uart_can.recv()
        # if ret:
        #     print('ret: {:d}  id:{:x} buf:{:s}'.format(ret, id, str(buf)))

        # sleep(1)

        # print('getting rpm from OBD2')
        # ret, __rpm = obd2.getRPM()
        # if(ret):
        #     strrpm = "RPM: {:d} rpm [{:d}]".format(__rpm, counter)
        #     print(strrpm)
        # else:
        #     print('getting rpm from OBD2 fail')

        sleep_ms(500)
        counter += 1
        
        pass

if __name__ == "__main__":
    main()




# class OBD2:
#     STANDARD_CAN_11BIT = 1       # That depands on your car. some 1 some 0.

#     PID_ENGIN_PRM = 0x0C
#     PID_VEHICLE_SPEED = 0x0D
#     PID_COOLANT_TEMP = 0x05

#     def __init__(self, uart_can: lib.serial_can_module.Serial_CAN):
#         self.__uart_can = uart_can
#         if self.STANDARD_CAN_11BIT:
#             self.CAN_ID_PID = 0x7DF
#         else:
#             self.CAN_ID_PID = 0x18db33f1

#         if self.STANDARD_CAN_11BIT:
#             self.mask = [
#                 0, 0x7FC,                # ext, maks 0
#                 0, 0x7FC,                # ext, mask 1
#             ]

#             self.filt = [
#                 0, 0x7E8,                # ext, filt 0
#                 0, 0x7E8,                # ext, filt 1
#                 0, 0x7E8,                # ext, filt 2
#                 0, 0x7E8,                # ext, filt 3
#                 0, 0x7E8,                # ext, filt 4
#                 0, 0x7E8,                # ext, filt 5
#             ]

#         else:
#             self.mask = [
#                 1, 0x1fffffff,               # ext, maks 0
#                 1, 0x1fffffff,
#             ]

#             self.filt = [

#                 1, 0x18DAF110,                # ext, filt
#                 1, 0x18DAF110,                # ext, filt 1
#                 1, 0x18DAF110,                # ext, filt 2
#                 1, 0x18DAF110,                # ext, filt 3
#                 1, 0x18DAF110,                # ext, filt 4
#                 1, 0x18DAF110,                # ext, filt 5
#             ]

#     def set_mask_filt(self) -> bool:
#         # TODO: debug this
#         # set mask, set both the mask to 0x3ff
#         ret = True
#         print('setMask:' + str(self.mask))
#         if(self.__uart_can.setMask(self.mask)):
#             print(" - set mask ok")
#         else:
#             print(" - set mask fail")
#             return False

#         # set filter, we can receive id from 0x04 ~ 0x09
#         print('setFilt:' + str(self.filt))
#         if(self.__uart_can.setFilt(self.filt)):
#             print(" - set filt ok")
#         else:
#             print(" - set filt fail")
#             return False
#         return True

#     def sendPid(self, __pid):
#         tmp = [0x02, 0x01, __pid, 0, 0, 0, 0, 0]

#         if self.STANDARD_CAN_11BIT:
#             self.__uart_can.send(self.CAN_ID_PID, False,
#                                  False, 8, tmp)   # SEND TO ID:0X55
#         else:
#             self.__uart_can.send(self.CAN_ID_PID, True,
#                                  False, 8, tmp)   # SEND TO ID:0X55

#     def getRPM(self):
#         rpm = 0
#         self.sendPid(OBD2.PID_ENGIN_PRM)
#         __timeout = millis()

#         while (millis()-__timeout < 1000):      # 1s time out
#             id = 0
#             buf = [b'0x00'] * 8

#             [res, id, buf] = self.__uart_can.recv()

#             if(res):                # check if get data
#                 if(buf[1] == 0x41):
#                     rpm = int((256*int(buf[3])+int(buf[4]))/4)
#                     return [1, rpm]

#         return [0, rpm]


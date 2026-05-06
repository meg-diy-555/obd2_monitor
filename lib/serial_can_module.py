
import RPi.GPIO as GPIO
import time
import serial
from enum import Enum


# NOTICE
# set __is_initialize_config is True
# to configure Serial CAN moudel.
# (only first time. setting is hold if you turn off the module.)

__is_initialize_config = False

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
    return (time.time_ns() / 100)


class Serial_CAN:
    class SerialBaudRateIndex(Enum):
        """
        Serial Baud Rate Constants
        """
        SERIAL_RATE_INDEX_9600 = 0
        SERIAL_RATE_INDEX_19200 = 1
        SERIAL_RATE_INDEX_38400 = 2
        # SERIAL_RATE_INDEX_57600 = 3
        SERIAL_RATE_INDEX_115200 = 4
        
        def to_baudrate(self) -> int:
            """Convert the enum value to the corresponding baud rate.
            Returns
            -------
            int
                The baud rate corresponding to the enum value.
            """
            self.serial_baud_rate = [
                Serial_CAN.SerialBaudRate.SERIAL_RATE_9600_BPS,
                Serial_CAN.SerialBaudRate.SERIAL_RATE_19200_BPS,
                Serial_CAN.SerialBaudRate.SERIAL_RATE_38400_BPS,
                0,  # SerialBaudRate.SERIAL_RATE_57600_BPS,
                Serial_CAN.SerialBaudRate.SERIAL_RATE_115200_BPS]
            
            if self.value < 0 or self.value >= len(self.serial_baud_rate):
                raise ValueError("Invalid SerialBaudRateIndex value")
            return self.serial_baud_rate[self.value].value
        
    class SerialBaudRate(Enum):
        """Serial Baud Rate Constants
        """
        SERIAL_RATE_9600_BPS = 9600
        SERIAL_RATE_19200_BPS = 19200
        SERIAL_RATE_38400_BPS = 38400
        # SERIAL_RATE_57600_BPS = 57600
        SERIAL_RATE_115200_BPS = 115200
        
        

        
    class CanRateIndex(Enum):
        """
        CAN Baud Rate Constants
        """
        CAN_RATE_5k = 1
        CAN_RATE_10k = 2
        CAN_RATE_20k = 3
        CAN_RATE_25k = 4
        CAN_RATE_31_2k = 5
        CAN_RATE_33k = 6
        CAN_RATE_40k = 7
        CAN_RATE_50k = 8
        CAN_RATE_80k = 9
        CAN_RATE_83_3k = 10
        CAN_RATE_95k = 11
        CAN_RATE_100k = 12
        CAN_RATE_125k = 13
        CAN_RATE_200k = 14
        CAN_RATE_250k = 15
        CAN_RATE_500k = 16
        CAN_RATE_666k = 17
        CAN_RATE_1000k = 18
        
        
    def __init__(self, serial_port_id: int, uart_baud_rate_index: SerialBaudRateIndex = SerialBaudRateIndex.SERIAL_RATE_INDEX_38400, timeout:int = 1) -> None:
        """
        Initialize the Serial_CAN instance.
        Parameters
        ----------
        serial_port_id : int
            The ID of the serial port to use.
        uart_baud_rate_index : SerialBaudRateIndex, optional
            The index of the baud rate to use (default is SERIAL_RATE_INDEX_38400).
        timeout : int, optional
            Timeout for the serial communication in seconds (default is 1).
        Returns
        -------
        None
        """
        self.set_uart_parameters(serial_port_id, uart_baud_rate_index, timeout)
        pass
    
    def set_uart_parameters(self, serial_port_id: int, uart_baud_rate_index: SerialBaudRateIndex = SerialBaudRateIndex.SERIAL_RATE_INDEX_38400, timeout_s:int = 1) -> None:
        """
        Set UART parameters for the Serial_CAN instance.
        
        Parameters
        ----------
        serial_port_id : int
            The ID of the serial port to use.
        uart_baud_rate_index : SerialBaudRateIndex, optional
            The index of the baud rate to use (default is SERIAL_RATE_INDEX_38400).
        timeout : int, optional
            Timeout for the serial communication in seconds (default is 1).
        
        Returns
        -------
        None
        """
        self.serial_port_id = serial_port_id
        self.uart_baud_rate_index = uart_baud_rate_index
        self.uart_baud_rate = uart_baud_rate_index.to_baudrate()
        self.timeout_s = timeout_s

    # private:
    def __cmdOk(self, cmd: str, is_debug :bool = False) -> bool:

        if is_debug:
            print('sending cmdOk:' + cmd)
        ret = False

        timer_start_ms = millis()
        cmd_send = cmd + "\r\n"
        self.uart.write(f"{cmd_send}".encode('utf-8'))
        diff_time_ms = 0
        is_recv_code = False
        while(1):
            diff_time_ms = millis() - timer_start_ms
            if(diff_time_ms > self.timeout_s * 1000):
                if is_debug:
                    print('- cmdOk:' + cmd +
                          ' Timed out [' + str(diff_time_ms) + ' ms]')
                return False

            str_tmp = None
            str_tmp = self.uart.read()
            timer_start_ms = millis()

            if is_debug:
                if str_tmp is not None:
                    print('- cmdOk:' + cmd + ',str_tmp:"' +
                            str(str_tmp) + '" [' + str(diff_time_ms) + ' ms]')

            if str_tmp is not None:
                tokens = str_tmp.split(b'\r\n')
                len = 0
                for token in tokens:
                    # str_len = len(token)
                    # str_tail = token[str_len-2:str_len]
                    # str_tail2 = token[str_len-5:str_len]

                    if is_debug:
                        print(f'- cmdOk:{cmd:s}, str_tail[{len:d}]:"{str(token):s}" [{diff_time_ms:d} ms]')
                        print("- True" if (token) ==  (b'OK') else "- False")
                    if (token) == (b'OK'):
                        if is_debug:
                            print('- cmdOk:' + cmd +
                                  ' OK [' + str(diff_time_ms) + ' ms]')
                        self.__clear()
                        ret = True
                        is_recv_code = True
                    elif (tokens) == (b'ERROR'):
                        is_recv_code = True
                    else:
                        if is_debug:
                            # print('- cmdOk:' + cmd +
                            #       ' Failed [' + str(diff_time) + ' ms]')
                            pass
                        pass
                    if is_recv_code:
                        break
                    len += 1
            else:
                if is_debug:
                    # print('- cmdOk:' + cmd +
                    #       ' Failed [' + str(diff_time) + ' ms]')
                    pass
                pass

            if is_recv_code:
                break

        if is_debug:
            if ret:
                print(' - cmdOk:' + cmd + ' OK (' + str(str_tmp) +
                      ') [' + str(diff_time_ms) + ' ms]')
            else:
                print(' - cmdOk:' + cmd + ' Failed (' +
                      str(str_tmp) + ')[' + str(diff_time_ms) + ' ms]')
        return ret

    def __enterSettingMode(self):
        print("__enterSettingMode (without check ACK)")
        self.uart.write(b'+++')
        self.__clear()
        return True

    def __exitSettingMode(self):
        print("__exitSettingMode")
        ret = self.__cmdOk("AT+Q")
        self.__clear()
        print("done(" + ("True" if ret else "False") + ")")
        return ret

    def __clear(self):

        timer_start_ms = millis()
        while(1):
            if(millis()-timer_start_ms > 50):
                return
            if self.uart is not None:
                buff = self.uart.read()
                if len(buff) <= 0:
                    break
            timer_start_ms = millis()
                    

    # def __selfBaudRate(self,  baudrate: int):
    #     self.__uart = UART(self.__id, baudrate=baudrate,
    #                        tx=self.__tx, rx=self.__rx)

    # __str_tmp = ""
    # __softwareSerial = None
    # __hardwareSerial = None
    # __canSerial = None

    def close(self):
        self.uart.close()
        self.uart = None

    # public:

    def begin(self) -> None:
        self.uart = serial.Serial(f'/dev/serial{self.serial_port_id}', baudrate=self.uart_baud_rate_index.to_baudrate(), timeout=self.timeout_s)
        # self.__uart.open()
        if not self.uart.is_open:
            print("Failed to open serial port")
            raise Exception("Serial port not opened")
        print("Serial port opened successfully")
        pass

    def change_can_rate(self, can_rate_index: CanRateIndex) -> bool:
        """
        Set CAN BaudRate
        ----------
        rate : int
            CAN BaudRate
                value	    01	02	03	04	05	    06	07	08	09	10	    11	12	13	14	15	16	17	18
                rate(kb/s)	5	10	20	25	31.2	33	40	50	80	83.3	95	100	125	200	250	500	666	1000

        Returns
        -------
        None
        """
        self.__enterSettingMode()
        str_tmp = "AT+C={:02d}".format(can_rate_index.value)
        ret = self.__cmdOk(str_tmp)
        self.__exitSettingMode()

        return ret

    def change_serial_baudrate(self, baud_rate_index_to_change: SerialBaudRateIndex, baud_rate_index_now: SerialBaudRateIndex = -1) -> bool:

        ret = False

        print(f"baudRate  baud_rbaud_rate_index_to_changeate_to_change: {baud_rate_index_to_change.to_baudrate()}, baud_rate_index_now: {baud_rate_index_now.to_baudrate()} ")

        self.__enterSettingMode()
        print(f"changin UART baud rate to {baud_rate_index_to_change.to_baudrate()} bps...")
        str_tmp = "AT+S={:d}".format(baud_rate_index_to_change.value)
        self.__cmdOk(str_tmp, True)
        self.close()
        self.set_uart_parameters(
            self.serial_port_id,
            baud_rate_index_to_change,
            self.timeout_s
        )
        self.begin()
        ret = self.__cmdOk("AT")

        if(ret):
            print("UART baudrate set to ")
            print(baud_rate_index_to_change.to_baudrate())
        
        self.__exitSettingMode()

        print("change UART rate done")
        return ret


    def send(self, id: int, ext: bool, rtrBit: bool,  len: int,  buf):
        """
        Send CAN Frame
        ----------
        id : int
            CAN ID (11bit or 29bit)
        ext : bool
            1: Extended CAN Frame
            0: Standard CAN Frame
        rtrBit : bool
            1: Remote CAN Frame
            0: Standard CAN Frame
        len: int
            Length of a CAN Frame
        buf: List[int]
            Data of a CAN Frame

        Returns
        -------
        None
        """
        dta = [0] * (6+len)
        dta[0] = id >> 24  # id3
        dta[1] = id >> 16 & 0xff   # id2
        dta[2] = id >> 8 & 0xff    # id1
        dta[3] = id & 0xff       # id0

        dta[4] = 1 if ext else 0
        dta[5] = 1 if rtrBit else 0

        for i in range(0, len):
            dta[6+i] = buf[i]

        bytes = [b'0x00'] * (6+len)

        for i in range(0, 6+len):
            bytes[i] = (dta[i]).to_bytes(1, 'little')
            self.uart.write(bytes[i])
            # print("Write UART[{:d}]: {:s}".format(i, str(bytes[i])))

    def flush_uart(self):
        while(self.uart.any()):
            tmp = self.uart.readline()
            print("flashing uart: " + str(tmp))


    # 0: no data
    # 1: get data
    def recv(self) -> list:
        #print("recv() called")
        id = 0
        buf = [b'0x00']*8
        if self.uart.any():
            timer_s = millis()
            len = 0
            dta = [b'0x00']*12

            # print("UART has some data.")

            while True:
                tmp = self.uart.read(12)
                if tmp is not None:
                    for b in tmp:
                        dta[len] = b
                        len += 1
                    print(
                        " - recv read: [{:s} (len={:d})] ".format(str(tmp), len))
                if(len == 12):
                    break

                if((millis()-timer_s) > 100):
                    print(" - recv() time out [1]")
                    # Reading 12 bytes should be faster than 10ms, abort if it takes longer, we loose the partial message in this case
                    return [False, id, dta]

                if(len == 12):  # Just to be sure, must be 12 here
                    __id = 0
                    for i in range(0, 4):  # Store the id of the sender
                        __id <<= 8
                        __id += int(dta[i])
                    id = __id

                    for i in range(0, 8):  # Store the message in the buffer
                        buf[i] = dta[i+4]

                    print(
                        " - recv() OK: ID:{:x}, DATA:{:s}".format(id, str(buf)))
                    self.write_bytes_to_sd('OK', dta)
                    return [True, id, buf]

                if((millis()-timer_s) > 10):
                    print(" - recv() time out [2]")
                    self.write_bytes_to_sd('NG2', dta)
                    self.flush_uart()
                    # Reading 12 bytes should be faster than 10ms, abort if it takes longer, we loose the partial message in this case
                    return [False, id, buf]
        else:
            # print("UART has NO data.")
            pass
        return [False, id, buf]

    def setMask(self, dta) -> bool:
        self.__enterSettingMode()
        for i in range(0, 2):
            str_tmp = "AT+M=[{:d}][{:d}][{:08X}]\r\n\0".format(
                i, dta[2*i], dta[1+2*i])

            # print("setMaxk(" + str_tmp + ")")

            if not self.__cmdOk(str_tmp):
                print("mask fail - " + str(i))
                self.__exitSettingMode()
                return False
            self.__clear()
            sleep_ms(10)
        self.__exitSettingMode()
        return True

    def setFilt(self, dta):
        self.__enterSettingMode()
        for i in range(0, 6):
            str_tmp = "AT+F=[{:d}][{:d}][{:08X}]\r\n\0".format(
                i, dta[2*i], dta[1+2*i])
            # print("setFilt(" + str_tmp + ")")
            self.__clear()
            if not self.__cmdOk(str_tmp):
                print("filt fail at - " + str(i))
                self.__exitSettingMode()
                return False
            self.__clear()
            sleep_ms(10)
        self.__exitSettingMode()
        return True

    # def setFilt(self, dta):
    #     pass

    # def factorySetting(self):
    #     pass

    # def debugMode(self):
    #     pass

    # Constants:
    CAN_RATE_5 = 1
    CAN_RATE_10 = 2
    CAN_RATE_20 = 3
    CAN_RATE_25 = 4
    CAN_RATE_31_2 = 5
    CAN_RATE_33 = 6
    CAN_RATE_40 = 7
    CAN_RATE_50 = 8
    CAN_RATE_80 = 9
    CAN_RATE_83_3 = 10
    CAN_RATE_95 = 11
    CAN_RATE_100 = 12
    CAN_RATE_125 = 13
    CAN_RATE_200 = 14
    CAN_RATE_250 = 15
    CAN_RATE_500 = 16
    CAN_RATE_666 = 17
    CAN_RATE_1000 = 18


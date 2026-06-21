# Raspberry Pi 5 のI2C (ch1)を使ってI2C CANモジュールを制御するクラス
import smbus2
from enum import Enum
import time
import os

class CAN_MSG:
    def __init__(self, id:int=0, ext:int=0, length:int=0, data:list=[]):
        self.id = id
        self.ext = ext
        self.length = length
        self.data = data
    
    def data_to_hex_str(self):
        """Convert data bytes to a hexadecimal string."""
        return ' '.join(f'{byte:02x}' for byte in self.data)

    def __str__(self):
        return f"CAN_MSG(id={self.id:x}, ext={self.ext}, length={self.length}, data={self.data_to_hex_str()})"
    
    
    def is_valid_can_msg(self) -> bool:
        return isinstance(self, CAN_MSG) and 0 <= self.length <= 8

class I2C_CAN:
    
    DEFAULT_I2C_ADDR    = 0X25
    DEFAULT_RETRY_COUNT = 3
    DEFAULT_RETRY_WAIT_SEC = 0.05
    DNUM_MAX = 16  # module buffer size (Longan datasheet)

    def __init__(self, i2c_ch: int=1, i2c_addr: int =DEFAULT_I2C_ADDR, event_can_received=None, is_silent=True):
        """Initialize the I2C_CAN class.
        Args:
            i2c_ch (int): I2C channel number (default is 1).
            i2c_addr (int): I2C address of the CAN module (default is 0x25).
        """
        self.i2c_ch = i2c_ch
        self.i2c_can_address = i2c_addr
        self.smbus = smbus2.SMBus(i2c_ch)  # Adjust the bus number as needed
        self.debug_i2c = os.getenv("I2C_CAN_DEBUG", "0") == "1"
        self._debug_fail_count = 0
        # Zero/Zero2 W ではレジスタ指定後の待ち時間が短いと read が失敗しやすいため、
        # 安全側の既定値を 20ms にする（必要なら環境変数で上書き可能）。
        self.read_settle_sec = float(os.getenv("I2C_CAN_READ_SETTLE_SEC", "0.02"))
        self.event_can_received = event_can_received
        self.is_silent = is_silent
        self.last_recv_raw = None
    
    def init_i2c_can(self, i2c_ch: int=1, i2c_addr: int =DEFAULT_I2C_ADDR, is_silent=True):
        """Initialize I2C-CAN module with retry."""
        last_err = None
        for attempt in range(1, self.DEFAULT_RETRY_COUNT + 1):
            try:
                i2c_can = I2C_CAN(i2c_ch, i2c_addr)
                i2c_can.begin(self.DEFAULT_I2C_BAUD)
                time.sleep(0.05)
                if not is_silent: print(
                    f"I2C-CAN initialized: ch={i2c_ch}, addr=0x{i2c_addr:02X}, baud={self.DEFAULT_I2C_BAUD}"
                )
                return i2c_can
            except OSError as err:
                last_err = err
                print(
                    f"I2C init failed ({attempt}/{self.DEFAULT_RETRY_COUNT}): {err}. "
                    f"retry in {self.DEFAULT_RETRY_WAIT_SEC:.1f}s"
                )
                time.sleep(self.DEFAULT_RETRY_WAIT_SEC)
        raise last_err
    
    def check_i2c_can_thread(self, is_silent=True):
        """I2C CAN thread."""
        global data, logfile, prev_valid_data
        i2c_error_count = 0
        try:
            while True:
                try:
                    while True:
                        size = self.check_receive()
                        if size <= 0:
                            break
                        msg = self.read_can()
                        if msg is not None and msg.is_valid_can_msg():
                            data = msg
                            prev_valid_data = msg
                            if self.event_can_received:
                                self.event_can_received(msg)
                            elif not is_silent:
                                print(f"CAN [{msg.id:03X}] {msg.data_to_hex_str()}")
                        elif self.debug_i2c:
                            print(f"I2C_CAN debug: DNUM={size}, read failed or invalid frame")
                    i2c_error_count = 0
                except OSError as err:
                    i2c_error_count += 1
                    data = None
                    if i2c_error_count == 1 or i2c_error_count % 10 == 0:
                        if not is_silent:
                            print(f"I2C read failed ({i2c_error_count}): {err}")
                except Exception as err:
                    data = None
                    if not is_silent:
                        print(f"check_i2c_can_thread error: {err}")
                time.sleep(0.01)
        except KeyboardInterrupt:
            pass
        
    def begin(self, speedset) -> None:
        """Initialize CAN baud rate (Seeed/Longan I2C-CAN module)."""
        self.__set_reg(self.I2C_CAN_REG.REG_BAUD, [speedset])
        time.sleep(0.1)
        # DNUM 読み取りで I2C 通信を確認（BAUD 読み戻しは 0 になることがあるため使わない）
        self.__get_reg(self.I2C_CAN_REG.REG_DNUM, 1)
        if self.debug_i2c:
            try:
                baud = self.__get_reg(self.I2C_CAN_REG.REG_BAUD, 1)[0]
                print(f"I2C_CAN debug: baud readback={baud}, wrote={speedset}")
            except OSError as err:
                print(f"I2C_CAN debug: baud readback failed: {err}")

    def init_obd_filters(self) -> None:
        """Configure MCP2515 filters for OBD-II ECU responses (ID 0x7E8-0x7EF)."""
        self.init_Mask(0, 0, 0x7FC)
        self.init_Mask(1, 0, 0x7FC)
        for num in range(6):
            self.init_Filt(num, 0, 0x7E8)

    def init_accept_all_filters(self) -> None:
        """Accept all standard 11-bit CAN IDs (mask=0: all bits don't care)."""
        self.init_Mask(0, 0, 0)
        self.init_Mask(1, 0, 0)
        for num in range(6):
            self.init_Filt(num, 0, 0)
        
    def __set_reg(self, reg, data: list) -> None:
        """Write data to a specific register of the I2C CAN module.
        Args:
            reg (I2C_CAN_REG): The register to write to.
            data (list): List of data bytes to write.
        Returns:
            None
        """
        data = bytearray(data)
        if len(data) == 1:
            self.smbus.write_byte_data(self.i2c_can_address, reg.value, data[0])
        else:
            self.smbus.write_i2c_block_data(self.i2c_can_address, reg.value, data)
        
    def __read_reg_bytes(self, reg, length: int) -> list:
        """Write register pointer, then read bytes in one I2C transaction (Wire.requestFrom)."""
        last_error = None
        for attempt in range(self.DEFAULT_RETRY_COUNT):
            # Primary: write reg (stop) → single read transaction (Arduino IIC_CAN_GetReg)
            try:
                self.smbus.write_byte(self.i2c_can_address, reg.value)
                time.sleep(self.read_settle_sec)
                read_msg = smbus2.i2c_msg.read(self.i2c_can_address, length)
                self.smbus.i2c_rdwr(read_msg)
                return list(read_msg)
            except OSError as err:
                last_error = err

            # Fallback: repeated-start write reg + read
            try:
                write_msg = smbus2.i2c_msg.write(self.i2c_can_address, [reg.value])
                read_msg = smbus2.i2c_msg.read(self.i2c_can_address, length)
                self.smbus.i2c_rdwr(write_msg, read_msg)
                return list(read_msg)
            except OSError as err:
                last_error = err

            # Fallback: SMBus block read
            try:
                return self.smbus.read_i2c_block_data(self.i2c_can_address, reg.value, length)
            except OSError as err:
                last_error = err
                if attempt < self.DEFAULT_RETRY_COUNT - 1:
                    time.sleep(self.DEFAULT_RETRY_WAIT_SEC)

        raise last_error

    def __get_reg(self, reg, len:int) -> list:
        """Read register (Longan/Seeed I2C-CAN)."""
        return self.__read_reg_bytes(reg, len)

    def __read_recv_reg(self) -> list:
        """Read 16-byte RECV register."""
        return self.__read_reg_bytes(self.I2C_CAN_REG.REG_RECV, 16)
        
    def send_can(self, id:int, ext:int, len:int, data:list) -> None:
        """Send CAN message to the I2C CAN module.
        Args:
            id (int): CAN ID (0-0xFFFFFFFF)
            ext (int): 0 for standard CAN ID, 1 for extended CAN ID
            len (int): Length of the data (0-8)
            data (list): Data bytes to send (list of integers)
        Returns:
            None
        """
        buff = [
            0xff & (id >> 24),
            0xff & (id >> 16),
            0xff & (id >> 8),
            0xff & (id >> 0),
            ext,
            0,  # rtr
            len,
        ]
        buff.extend(data[:len])
        while len(buff) < 15:
            buff.append(0)
        buff.append(self.__makeCheckSum(buff))
        self.__set_reg(self.I2C_CAN_REG.REG_SEND, buff)
        
    def __makeCheckSum(self, dta:list):
        """Calculate checksum for the given data.
        Args:
            dta (list): List of data bytes.
        Returns:
            int: Checksum value.
        """
        sum = 0
        for elem in dta:
            sum += elem        
        if(sum > 0xff):
            sum = ~sum
            sum += 1        
        sum  = sum & 0xff
        return sum
    
    def read_can_raw(self) -> list:
        """Read raw 16-byte RECV buffer (for debug)."""
        return self.__read_recv_reg()

    def read_can(self) -> CAN_MSG | None:
        """Read a CAN message from the I2C CAN module.
        Returns:
            CAN_MSG: An instance of the CAN_MSG class containing the received message.
            None: If checksum is invalid or length is invalid.
        """
        data = self.__read_recv_reg()
        self.last_recv_raw = data
        if all(b == 0 for b in data):
            return None
        # I2C 誤読時の 0xFF パディングを除外
        if len(data) == 16 and data[1] == 0xFF and all(b == 0xFF for b in data[1:]):
            return None

        id = 0
        
        if self.debug_i2c:
            print(f"read_can: {data}")
        
        checksum = self.__makeCheckSum(data[:-1])
        if checksum != data[-1]:
            if self.debug_i2c:
                print(f"Checksum error: raw={data}, calc=0x{checksum:02X}, got=0x{data[-1]:02X}")
            return None
        id += data[0]
        id <<= 8
        id += data[1]
        id <<= 8
        id += data[2]
        id <<= 8
        id += data[3]
        
        ext = data[4]
        rtr = data[5]
        length = data[6]
        if length < 0 or length > 8:
            if self.debug_i2c:
                print("Invalid length")
            return None
        data = data[7:7+length]
        return CAN_MSG(id, ext, length, data)
    

    def check_receive(self) -> int:
        """Read the number of buffered CAN frames (0-16)."""
        for attempt in range(self.DEFAULT_RETRY_COUNT):
            try:
                count = self.__read_reg_bytes(self.I2C_CAN_REG.REG_DNUM, 1)[0]
            except OSError as err:
                if self.debug_i2c:
                    print(f"I2C_CAN debug: DNUM read error: {err}")
                time.sleep(self.read_settle_sec)
                continue
            if 0 <= count <= self.DNUM_MAX:
                return count
            if self.debug_i2c:
                print(f"I2C_CAN debug: invalid DNUM={count}, retry {attempt + 1}")
            time.sleep(self.read_settle_sec)
        return 0
    
    def init_Mask(self, num: int, ext: int, ulData: int):
        dta = [
            ext,
            0xff & (ulData >> 24),
            0xff & (ulData >> 16),
            0xff & (ulData >> 8),
            0xff & (ulData >> 0),
        ]
        mask = self.I2C_CAN_REG.REG_MASK0 if num == 0 else self.I2C_CAN_REG.REG_MASK1
        self.__set_reg(mask, dta)
        time.sleep(0.050)

    def init_Filt(self, num: int, ext: int, ulData: int):
        dta = [
            ext,
            0xff & (ulData >> 24),
            0xff & (ulData >> 16),
            0xff & (ulData >> 8),
            0xff & (ulData >> 0),
        ]
        filt_regs = (
            self.I2C_CAN_REG.REG_FILT0,
            self.I2C_CAN_REG.REG_FILT1,
            self.I2C_CAN_REG.REG_FILT2,
            self.I2C_CAN_REG.REG_FILT3,
            self.I2C_CAN_REG.REG_FILT4,
            self.I2C_CAN_REG.REG_FILT5,
        )
        if num < 0 or num >= len(filt_regs):
            raise ValueError(f"filter num must be 0-5, got {num}")
        self.__set_reg(filt_regs[num], dta)
        time.sleep(0.050)


    class I2C_CAN_REG(Enum):
        REG_ADDR            = 0X01
        REG_DNUM            = 0x02
        REG_BAUD            = 0X03
        REG_MASK0           = 0X60
        REG_MASK1           = 0X65
        REG_FILT0           = 0X70
        REG_FILT1           = 0X80
        REG_FILT2           = 0X90
        REG_FILT3           = 0XA0
        REG_FILT4           = 0XB0
        REG_FILT5           = 0XC0
        REG_SEND            = 0X30
        REG_RECV            = 0X40
        REG_ADDR_SET        = 0X51
    
    class I2C_CAN_BAUD(Enum):
        CAN_5KBPS           = 1
        CAN_10KBPS          = 2
        CAN_20KBPS          = 3
        CAN_25KBPS          = 4 
        CAN_31K25BPS        = 5
        CAN_33KBPS          = 6
        CAN_40KBPS          = 7
        CAN_50KBPS          = 8
        CAN_80KBPS          = 9
        CAN_83K3BPS         = 10
        CAN_95KBPS          = 11
        CAN_100KBPS         = 12
        CAN_125KBPS         = 13
        CAN_200KBPS         = 14
        CAN_250KBPS         = 15
        CAN_500KBPS         = 16
        CAN_666KBPS         = 17
        CAN_1000KBPS        = 18
        
    class I2C_CAN_STATUS(Enum):
        CAN_OK              = (0)
        CAN_FAILINIT        = (1)
        CAN_FAILTX          = (2)
        CAN_MSGAVAIL        = (3)
        CAN_NOMSG           = (4)
        CAN_CTRLERROR       = (5)
        CAN_GETTXBFTIMEOUT  = (6)
        CAN_SENDMSGTIMEOUT  = (7)
        CAN_FAIL            = (0xff)
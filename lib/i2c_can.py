# Raspberry Pi 5 のI2C (ch1)を使ってI2C CANモジュールを制御するクラス
import smbus2
from enum import Enum
import time

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
    
class I2C_CAN:
    
    DEFAULT_I2C_ADDR    = 0X25

    def __init__(self, i2c_ch: int=1, i2c_addr: int =DEFAULT_I2C_ADDR):
        """Initialize the I2C_CAN class.
        Args:
            i2c_ch (int): I2C channel number (default is 1).
            i2c_addr (int): I2C address of the CAN module (default is 0x25).
        """
        self.i2c_ch = i2c_ch
        self.i2c_can_address = i2c_addr
        self.smbus = smbus2.SMBus(i2c_ch)  # Adjust the bus number as needed
        
    def begin(self, speedset) -> None:
        """Initialize the I2C CAN module with the specified speed.
        Args:
            speedset (I2C_CAN_BAUD): Speed setting for the CAN module.
        Returns:
            None
        """
        self.__set_reg(self.I2C_CAN_REG.REG_BAUD, [speedset])
        time.sleep(0.010)
        
    def __set_reg(self, reg, data: list) -> None:
        """Write data to a specific register of the I2C CAN module.
        Args:
            reg (I2C_CAN_REG): The register to write to.
            data (list): List of data bytes to write.
        Returns:
            None
        """
        data = bytearray(data)
        self.smbus.write_i2c_block_data(self.i2c_can_address, reg.value, data)
        
    def __get_reg(self, reg, len:int) -> int:
        """Read data from a specific register of the I2C CAN module.
        Args:
            reg (I2C_CAN_REG): The register to read from.
            len (int): Number of bytes to read.
        Returns:
            list: List of data bytes read from the register.
        """
        data = self.smbus.read_i2c_block_data(self.i2c_can_address, reg.value, len)
        return data
        
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
            0, #rtr
            len
        ]
        buff = buff+data
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
    
    def read_can(self) -> CAN_MSG:
        """Read a CAN message from the I2C CAN module.
        Returns:
            CAN_MSG: An instance of the CAN_MSG class containing the received message.
        """
        """Read a CAN message from the I2C CAN module.
        Returns:
            CAN_MSG: An instance of the CAN_MSG class containing the received message.
        """
        data = self.__get_reg(self.I2C_CAN_REG.REG_RECV, 16)
        id = 0
        
        checksum = self.__makeCheckSum(data[:-1])
        if checksum != data[-1]:
            print("Checksum error")
            return []
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
        if 8 < length < 0:
            print("Invalid length")
            return []
        data = data[7:7+length]
        return CAN_MSG(id, ext, length, data)
    

    def check_receive(self) -> int:
        """Read the size of stored CAN frames in the I2C CAN module.
        Returns:
            int: The number of stored CAN frames.
        """
        """Read the size of stored CAN frames in the I2C CAN module.
        Returns:
            int: The number of stored CAN frames.
        """
        data = self.__get_reg(self.I2C_CAN_REG.REG_DNUM, 1)
        return data[0]
    
    def init_Mask(self, num: int, ext: int, ulData: int):
        """Initialize a CAN mask in the I2C CAN module.
        Args:
            num (int): Mask number (0 or 1).
            ext (int): 0 for standard CAN ID, 1 for extended CAN ID.
            ulData (int): The mask value (0-0xFFFFFFFF).
        Returns:
            None
        """
        dta = []        
        dta[0] = ext
        dta[1] = 0xff & (ulData >> 24)
        dta[2] = 0xff & (ulData >> 16)
        dta[3] = 0xff & (ulData >> 8)
        dta[4] = 0xff & (ulData >> 0)
        mask = self.I2C_CAN_REG.REG_MASK0 if (num == 0) else  self.I2C_CAN_REG.REG_MASK1
        self.__set_reg(mask, dta)
        time.sleep(0.050)


    def init_Filt(self, num: int, ext: int, ulData: int):
        """Initialize a CAN filter in the I2C CAN module.
        Args:
            num (int): Filter number (0-5).
            ext (int): 0 for standard CAN ID, 1 for extended CAN ID.
            ulData (int): The filter value (0-0xFFFFFFFF).
        Returns:
            None
        """
        dta = []
        dta[0] = ext
        dta[1] = 0xff & (ulData >> 24)
        dta[2] = 0xff & (ulData >> 16)
        dta[3] = 0xff & (ulData >> 8)
        dta[4] = 0xff & (ulData >> 0)        
        filt = (7+num)*0x10
        self.__set_reg(filt, dta)
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
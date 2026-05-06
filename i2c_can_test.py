
import lib.i2c_can
import time

if __name__ == "__main__":
    # Example usage of the I2C_CAN class
    ch_i2c = 1  # I2C channel, adjust as needed
    i2c_can = lib.i2c_can.I2C_CAN(ch_i2c)
    
    while True:
        # Example of sending a CAN message
        id = 0x123
        ext = 0  # Standard CAN ID
        length = 8  # Length of the data
        data = [0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08]
        # i2c_can.send_can(id, ext, length, data)
        # print(".")        
        
        size = i2c_can.check_receive()  # Read the size of stored frames
        print("Stored frame size:", size)
        if size > 0:
            data = i2c_can.read_can()  # Read CAN messages
            print("Received CAN data:", data)
            
        
        time.sleep(0.1)  # Wait for a second before sending the next message

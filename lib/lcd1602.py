"""LCD1602 I2C interface for Raspberry Pi
This code is based on the New LiquidCrystal library for Raspberry Pi.
It provides a class to control an LCD1602 display over I2C.
It uses the smbus2 library for I2C communication.
It is designed to work with Raspberry Pi's I2C interface.

This code is based on Arduino's LiquidCrystal library and adapted for Raspberry Pi.
"""


import time
import smbus2
import logging
from enum import Enum

class LCD1602_COMMANDS(Enum):
    #commands
    LCD_CLEARDISPLAY = 0x01
    LCD_RETURNHOME = 0x02
    LCD_ENTRYMODESET = 0x04
    LCD_DISPLAYCONTROL = 0x08
    LCD_CURSORSHIFT = 0x10
    LCD_FUNCTIONSET = 0x20
    LCD_SETCGRAMADDR = 0x40
    LCD_SETDDRAMADDR = 0x80

class LCD1602_FLAGS_ENTRY(Enum):
    #flags for display entry mode
    LCD_ENTRYRIGHT = 0x00
    LCD_ENTRYLEFT = 0x02
    LCD_ENTRYSHIFTINCREMENT = 0x01
    LCD_ENTRYSHIFTDECREMENT = 0x00
    
class LCD1602_FLAGS_DISPLAY(Enum):
    #flags for display on/off control
    LCD_DISPLAYON = 0x04
    LCD_DISPLAYOFF = 0x00
    LCD_CURSORON = 0x02
    LCD_CURSOROFF = 0x00
    LCD_BLINKON = 0x01
    LCD_BLINKOFF = 0x00

class LCD1602_FLAGS_SHIFT(Enum):
    #flags for display/cursor shift
    LCD_DISPLAYMOVE = 0x08
    LCD_CURSORMOVE = 0x00
    LCD_MOVERIGHT = 0x04
    LCD_MOVELEFT = 0x00

class LCD1602_FLAGS_BITMODE(Enum):
    #flags for function set
    LCD_8BITMODE = 0x10
    LCD_4BITMODE = 0x00
    
class LCD1602_FLAGS_LINEMODE(Enum):
    LCD_2LINE = 0x08
    LCD_1LINE = 0x00

class LCD1602_FLAGS_DOTSIZE(Enum):
    LCD_5x10DOTS = 0x04
    LCD_5x8DOTS = 0x00
    
    
class LCD1602(object):
    
    DEFAULT_I2C_ADDR = 0x3E  # Default I2C address for the LCD1602
    def __init__(self, i2c_ch: int,
                line_mode: LCD1602_FLAGS_LINEMODE = LCD1602_FLAGS_LINEMODE.LCD_2LINE,
                dot_size: LCD1602_FLAGS_DOTSIZE = LCD1602_FLAGS_DOTSIZE.LCD_5x8DOTS,
                is_on: bool = True, lcd_addr:int = DEFAULT_I2C_ADDR):
        
        self.i2c_ch = i2c_ch
        self.smbus = smbus2.SMBus(i2c_ch)
        self.lcd_address = lcd_addr
        self.line = line_mode
        self.currline = 0
        self.control_flag = line_mode.value
        self.control_flag |= dot_size.value

        # wait for more than 15ms after VDD raise to 4.5V (from datasheet)
        time.sleep(0.050)
        
        # Function set
        self.command(LCD1602_COMMANDS.LCD_FUNCTIONSET.value | self.control_flag)
        time.sleep(0.004500) #wait more than 4.1ms
        
        #turn the display on with no cursor or blinking default
        self.display_mode = LCD1602_FLAGS_DISPLAY.LCD_DISPLAYON.value | LCD1602_FLAGS_DISPLAY.LCD_CURSOROFF.value | LCD1602_FLAGS_DISPLAY.LCD_BLINKOFF.value
        
        self.display()

        #clear it off
        self.clear()

        #Initialize to default text direction (for romance languages)
        self.display_mode = LCD1602_FLAGS_ENTRY.LCD_ENTRYLEFT.value | LCD1602_FLAGS_ENTRY.LCD_ENTRYSHIFTDECREMENT.value
        #set the entry mode
        self.command(LCD1602_COMMANDS.LCD_ENTRYMODESET.value | self.display_mode)  
        
    def close(self):
        """Close the I2C bus."""
        if self.smbus:
            self.smbus.close()
        self.smbus = None
        
    def clear(self):
        self.command(LCD1602_COMMANDS.LCD_CLEARDISPLAY.value)   #clear display, set cursor position to zero
        time.sleep(0.002)                  #this command takes a long time!
        
    def home(self):
        self.command(LCD1602_COMMANDS.LCD_RETURNHOME.value)     #set cursor position to zero
        time.sleep(0.002)                  #this command takes a long time!
        
    def setCursor(self, col, row):
        col = (col | 0x80) if row == 0 else (col | 0xc0)
        self.command(col)
        
    #Turn the display on/off (quickly)
    def no_display(self):
        self.control_flag &= ~LCD1602_FLAGS_DISPLAY.LCD_DISPLAYON.value
        self.command(LCD1602_COMMANDS.LCD_DISPLAYCONTROL.value  | self.control_flag)
        
    def display(self):
        self.control_flag |= LCD1602_FLAGS_DISPLAY.LCD_DISPLAYON.value
        self.command(LCD1602_COMMANDS.LCD_DISPLAYCONTROL.value  | self.control_flag)
        
    #Turns the underline cursor on/off
    def no_cursor(self):
        self.control_flag &= ~LCD1602_FLAGS_DISPLAY.LCD_CURSORON.value
        self.command(LCD1602_COMMANDS.LCD_DISPLAYCONTROL.value  | self.control_flag)
            
    def cursor(self):
        self.control_flag |= LCD1602_FLAGS_DISPLAY.LCD_CURSORON.value
        self.command(LCD1602_COMMANDS.LCD_DISPLAYCONTROL.value  | self.control_flag)
        
    #Turn on and off the blinking cursor    
    def no_blink(self):
        self.control_flag &= ~LCD1602_FLAGS_DISPLAY.LCD_BLINKON.value
        self.command(LCD1602_COMMANDS.LCD_DISPLAYCONTROL.value  | self.control_flag)
            
    def blink(self):
        self.control_flag |= LCD1602_FLAGS_DISPLAY.LCD_BLINKON.value
        self.command(LCD1602_COMMANDS.LCD_DISPLAYCONTROL.value  | self.control_flag)
             
        
    def autoscroll(self):
        self.control_flag |= LCD1602_FLAGS_ENTRY.LCD_ENTRYSHIFTINCREMENT.value
        self.command(LCD1602_COMMANDS.LCD_DISPLAYCONTROL.value  | self.control_flag)
        
    def no_autoscroll(self):
        self.control_flag &= ~LCD1602_FLAGS_ENTRY.LCD_ENTRYSHIFTINCREMENT.value
        self.command(LCD1602_COMMANDS.LCD_DISPLAYCONTROL.value  | self.control_flag)
        
    def create_char(self, location, charmap):
        location &= 0x07
        self.command(LCD1602_COMMANDS.LCD_SETCGRAMADDR.value | (location << 3))
        dta = bytearray([charmap])
        try:
            self.smbus.write_i2c_block_data(self.address, 0x40, dta)
        except OSError as e:
            logging.error(f"Error writing character map [{location}, {charmap}] to LCD: {e}")
            # raise e
        
    def command(self, command):
        bcommand = bytearray([command])
        try:
            self.smbus.write_i2c_block_data(self.lcd_address, 0x80, bcommand)
        except OSError as e:
            logging.error(f"Error writing command [{command}]to LCD: {e}")
            # raise e
        
    def write(self, command):
        command = bytearray([command])
        self.smbus.write_i2c_block_data(self.lcd_address, 0x40, command)
        
    def print(self, text):
        for char in text:
            self.write(ord(char))


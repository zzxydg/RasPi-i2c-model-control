import smbus
import sys
import getopt
import time

# I2C LCD address on Raspberry Pi
ADDRESS = 0x20

# commands
LCD_CLEARDISPLAY = 0x01
LCD_RETURNHOME = 0x02
LCD_ENTRYMODESET = 0x04
LCD_DISPLAYCONTROL = 0x08
LCD_CURSORSHIFT = 0x10
LCD_FUNCTIONSET = 0x20
LCD_SETCGRAMADDR = 0x40
LCD_SETDDRAMADDR = 0x80

# flags for display entry mode
LCD_ENTRYRIGHT = 0x00
LCD_ENTRYLEFT = 0x02
LCD_ENTRYSHIFTINCREMENT = 0x01
LCD_ENTRYSHIFTDECREMENT = 0x00

# flags for display on/off control
LCD_DISPLAYON = 0x04
LCD_DISPLAYOFF = 0x00
LCD_CURSORON = 0x02
LCD_CURSOROFF = 0x00
LCD_BLINKON = 0x01
LCD_BLINKOFF = 0x00

# flags for display/cursor shift
LCD_DISPLAYMOVE = 0x08
LCD_CURSORMOVE = 0x00
LCD_MOVERIGHT = 0x04
LCD_MOVELEFT = 0x00

# flags for function set
LCD_8BITMODE = 0x10
LCD_4BITMODE = 0x00
LCD_2LINE = 0x08
LCD_1LINE = 0x00
LCD_5x10DOTS = 0x04
LCD_5x8DOTS = 0x00

# flags for backlight control
LCD_BACKLIGHT = 0x08
LCD_NOBACKLIGHT = 0x00

# MCP23017 Register addresses
GPIOA = 0x12
GPIOB = 0x13

IODIRA = 0x00
IODIRB = 0x01

LCD_DELAY = 0.0003 #3ms

# control and  bits
REGISTER_SELECT_BIT = 0x08 # LCD Register select bit [GPB3]
ENABLE_BIT = 0x04 # LCD Enable bit [GPB2]

class MCP23017_LCDDriver:

    def __init__(self):
        #Default i2c bus
        self.bus = smbus.SMBus(0)
        self.LCD_Address = ADDRESS
        self.LCD_Command_Mode = 0x00
        self.LCD_Data_Mode = REGISTER_SELECT_BIT

        # Setup the Port directions
        self.bus.write_byte_data(self.LCD_Address, IODIRA, 0x00) # Set all of GPIOA to outputs
        self.bus.write_byte_data(self.LCD_Address, IODIRB, 0x00) # Set all of GPIOB to outputs

        #Initialize the screen.
        self.__initialize()

    def __initialize(self):

        # Init the LCD into a mode to accept programming
        self.__Write_HighNibble(0x30)
        time.sleep(0.05) #5ms

        self.__Write_HighNibble(0x30)
        time.sleep(LCD_DELAY)

        self.__Write_HighNibble(0x30)
        time.sleep(LCD_DELAY)

        self.__Write_HighNibble(0x20)
        time.sleep(LCD_DELAY)

        # Programme the LCD
        self.__Write_Command(LCD_FUNCTIONSET | LCD_2LINE | LCD_5x8DOTS | LCD_4BITMODE)
        self.__Write_Command(LCD_DISPLAYCONTROL | LCD_DISPLAYON)
        self.__Write_Command(LCD_CLEARDISPLAY)
        self.__Write_Command(LCD_ENTRYMODESET | LCD_ENTRYLEFT)
    
        time.sleep(0.5)
    
    def __fnwriteic2data(self, thebank, thedata):
        #print("fnwriteic2data(0x%02X, 0x%02X, 0x%02X)" % (theaddress, thebank, thedata))

        try:
            if thebank == 1:
                self.bus.write_byte_data(self.LCD_Address, GPIOA, thedata) # Write out the data, GPIOA
            else:
                self.bus.write_byte_data(self.LCD_Address, GPIOB, thedata) # Write out the data, GPIOB
        except:
            print("fnwriteic2data(): Error -- unable to writing to SMBus!")

        time.sleep(LCD_DELAY)
        return

    def __Write_Byte(self, the_byte, rs_flag):

        high_nibble = the_byte & 0xF0
        low_nibble = (the_byte << 4) & 0xF0

        if rs_flag == 1:

            # Write the high nibble
            self.__fnwriteic2data(1, high_nibble | REGISTER_SELECT_BIT)
            self.__fnwriteic2data(1, high_nibble | REGISTER_SELECT_BIT | ENABLE_BIT)
            self.__fnwriteic2data(1, high_nibble | REGISTER_SELECT_BIT)

            # Write the low nibble
            self.__fnwriteic2data(1, low_nibble | REGISTER_SELECT_BIT)
            self.__fnwriteic2data(1, low_nibble | REGISTER_SELECT_BIT | ENABLE_BIT)
            self.__fnwriteic2data(1, low_nibble | REGISTER_SELECT_BIT)

        else:

            # Write the high nibble
            self.__fnwriteic2data(1, high_nibble)
            self.__fnwriteic2data(1, high_nibble | ENABLE_BIT)
            self.__fnwriteic2data(1, high_nibble)

            # Write the low nibble
            self.__fnwriteic2data(1, low_nibble)
            self.__fnwriteic2data(1, low_nibble | ENABLE_BIT)
            self.__fnwriteic2data(1, low_nibble)

            # Clear the lines
            self.__fnwriteic2data(1, 0x00)

        return

    def __Write_HighNibble(self, the_byte):

        high_nibble = the_byte & 0xF0

        # Write the high nibble
        self.__fnwriteic2data(1, high_nibble)
        self.__fnwriteic2data(1, high_nibble | ENABLE_BIT)
        self.__fnwriteic2data(1, high_nibble)

        # Clear the lines
        self.__fnwriteic2data(1, 0x00)

        return

    def __Write_Data(self, data_byte):
        self.__Write_Byte(data_byte, 1)
        return;

    def __Write_Command(self, command_byte):
        self.__Write_Byte(command_byte, 0)
        return;


    def Display_String(self, string, line):
        if line == 1:
            self.__Write_Command(0x80) # line 1 DDRAM = 0x00
        elif line == 2:
            self.__Write_Command(0xC0) # line 2 DDRAM = 0x40
        else:
            print("LCD_Display_String(): Error -- invalid Line number!")

        for char in string:
            self.__Write_Data(ord(char))

        return

    def Clear_Screen(self):
        self.__Write_Command(LCD_CLEARDISPLAY)
        self.__Write_Command(LCD_RETURNHOME)
        return

    def POST(self):
        self.Clear_Screen()        
        self.Display_String("** MCP23017_LCDDriver.py POST routine **", 1)
        self.Display_String("time.time(%d)" % time.time(), 2)                                       
        return

# EOF

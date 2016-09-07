import smbus
import sys
import getopt
import time
from MCP23017_LCDDriver import MCP23017_LCDDriver

def main():

    LCD = MCP23017_LCDDriver()
    LCD.POST()
        
    return

if __name__ == '__main__':
    main()
    quit()
    exit()

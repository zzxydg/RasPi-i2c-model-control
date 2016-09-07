#!/usr/bin/python
# TITLE: I2C TEST PROGRAMME FOR EXTENSION BOARD
# DESCRIPTION: A programe that tests the points/segments connected to the extension board
# REVISION: 0.1, 24-Dec-2015, Initial revision

from ExtensionBoard_PointPowerDriver import ExtensionBoard_PointPowerDriver
import time

def main():

    print("main(): Starting up the board")
    ExtensionBoard = ExtensionBoard_PointPowerDriver(0x20, 0x27, False, True)

    i = 1
    j = 1

    while 1:       

        ExtensionBoard.TogglePoint(i)
        ExtensionBoard.TogglePoint(i)
        
        ExtensionBoard.ToggleSegment(j)
        time.sleep(1.0)
        ExtensionBoard.ToggleSegment(j)
        time.sleep(1.0)
        ExtensionBoard.ToggleSegment(j)
        time.sleep(1.0)
        
        print("\n")

        i += 1
        j += 1
        
        if i > 24:
            i = 1
        #endif
        
        if j > 8:
            j = 1
        #endif
                
        time.sleep(1.0)
    #endwhile

    return
#enddef

if __name__ == '__main__':
    main()
#endif    

#EOF

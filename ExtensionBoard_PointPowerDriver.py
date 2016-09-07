#!/usr/bin/python
#===============================================================================
# TITLE: EXTENSION BOARD POINT AND POWER DRIVER
# DESCRIPTION: A class the handles the business of switching the points and
# driving the relays to power the segments
# REVISION: 0.1, 08-Apr-2015, Initial revision in class format
# REVISION: 0.2, 12-Apr-2015, Initial revision ready for Raspbery Pi port
# REVISION: 0.3, 01-Oct-2015, Logic to introduce CDU recharge delay correctly
# REVISION: 0.4, 24-Dec-2015, Updated point tables to drive up-to 24 points using expander-board
# REVISION: 0.5, 27-Mar-2016, Increased RELAY_DELAY to 0.05 seconds (50ms) and CDU_RECHARGE to 2.0 (2000ms)
#===============================================================================

#===============================================================================
# MY TO DO:
# - None!
#===============================================================================

import smbus
import time
import traceback

POINT = 0x01
POWER = 0x02

POINT_POSA = 0x0
POINT_POSB = 0x1
RELAY_DELAY = 0.05
CDU_RECHARGE_DELAY = 2.0

POWER_OFF = 0x0
POWER_FWD = 0x1
POWER_REV = 0x2

BANK0 = 0x0
BANK0_ADDRESS = 0x12
BANK1 = 0x1
BANK1_ADDRESS = 0x13

# Declare array of 25 (24 points + blank) items and pre-int to zero
bPointDirection = [
    0,
    POINT_POSA, POINT_POSA, POINT_POSA, POINT_POSA, POINT_POSA, POINT_POSA, POINT_POSA, POINT_POSA,
    POINT_POSA, POINT_POSA, POINT_POSA, POINT_POSA, POINT_POSA, POINT_POSA, POINT_POSA, POINT_POSA,
    POINT_POSA, POINT_POSA, POINT_POSA, POINT_POSA, POINT_POSA, POINT_POSA, POINT_POSA, POINT_POSA
]

# Declare array of 8 items and pre-int to zero
bPowerDirection = [
    0,
    POWER_OFF,POWER_OFF,POWER_OFF,POWER_OFF,POWER_OFF,POWER_OFF,POWER_OFF,POWER_OFF
]

PointMask = [
    0,
    0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80
]

PowerSegmentMask = [
    0,
    0xFC, 0xF3, 0xCF, 0x3F, 0xFC, 0xF3, 0xCF, 0x3F
]

PowerSegmentOff  = [
    0,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
]

PowerSegmentFwd  = [
    0,
    0x01, 0x04, 0x10, 0x40, 0x01, 0x04, 0x10, 0x40
]

PowerSegmentRev  = [
    0,
    0x02, 0x08, 0x20, 0x80, 0x02, 0x08, 0x20, 0x80
]

# --------------------------------------------------------------------------------------------
# A class that implements simple function to drive the ExtensionBoard via I2C
# --------------------------------------------------------------------------------------------
class ExtensionBoard_PointPowerDriver:

    def __init__(self, ThePointBoardAddress, ThePowerBoardAddress, DoPost, PrintDebug):

        self.ThePointBoardAddress = ThePointBoardAddress
        self.ThePowerBoardAddress = ThePowerBoardAddress

        self.powerbank0 = 0x00
        self.powerbank1 = 0x00

        self.pointbank0 = 0x00
        self.pointbank1 = 0x00

        self.PrintDebug = PrintDebug

        try:
        # init the I2C board
        
            self.i2cbus = smbus.SMBus(1) # INIT the I2C Bus")

            self.i2cbus.write_byte_data(self.ThePointBoardAddress,0x00,self.pointbank0) # Set all of bank A to outputs")
            self.i2cbus.write_byte_data(self.ThePointBoardAddress,0x01,self.pointbank1) # Set all of bank B to outputs")

            self.i2cbus.write_byte_data(self.ThePowerBoardAddress,0x00,self.powerbank0) # Set all of bank A to outputs")
            self.i2cbus.write_byte_data(self.ThePowerBoardAddress,0x01,self.powerbank1) # Set all of bank B to outputs")

            if (DoPost == True):        
                self.POST()
            else:
                if self.PrintDebug == True:
                    print("POST skipped!")
                #endif
            #endif
        #endtry
        except Exception as e:
            print("FATAL Error initialising the SMBus [%s]" % str(e))
        #endexcept

        return
    #enddef

    def fnwriteic2data(self, pointorpower, thebank, thedata):

        theaddress = 0x00

        if pointorpower == POINT:
            theaddress = self.ThePointBoardAddress
        elif pointorpower == POWER:
            theaddress = self.ThePowerBoardAddress
        else:
            print("ERROR: Invalid pointorpower")
        #endif

        if self.PrintDebug == True:
            print("fnwriteic2data(theaddress=0x%02X, thebank=0x%02X, thedata=0x%02X)" % (theaddress, thebank, thedata))
        #endif

        try:
            if thebank == BANK1:
                self.i2cbus.write_byte_data(theaddress,BANK1_ADDRESS,thedata) # Write out the data to bank1")
            else:
                self.i2cbus.write_byte_data(theaddress,BANK0_ADDRESS,thedata) # Write out the data to bank0")
            #endif
        #endtry

        except Exception as e:
            print("FATAL Error writing to the SMBus\n[%s]" % str(e))
        #endexcept
        
        return
    #enddef

    def fnresetpointboard(self):
        if self.PrintDebug == True:
            print("fnresetpointboard(): Clear down all outputs")
        #endif
        self.fnwriteic2data( POINT, BANK0, 0x00)
        self.fnwriteic2data( POINT, BANK1, 0x00)
        self.pointbank0 = 0x00
        self.pointbank1 = 0x00        
        return
    #enddef

    def fnresetpowerboard(self):
        if self.PrintDebug == True:
            print("fnresetpowerboard(): Clear down all outputs")
        #endif
        self.fnwriteic2data( POWER, BANK0, 0x00)
        self.fnwriteic2data( POWER, BANK1, 0x00)
        self.powerbank0 = 0x00
        self.powerbank1 = 0x00
        return
    #enddef    

    def POST(self):
        # pulse each point to ensure none stuck AND pulse each relay segment to ensure to power drop-offs
        # switch all segment off to ensure no power is applied during the pulse test

        self.fnresetpowerboard()
        self.fntestpowerboard()
        self.fnresetpowerboard()
        
        self.fnresetpointboard()
        self.fntestpointboard()
        self.fnresetpointboard()
        
        return
    #enddef

    def fntestpointboard(self):

        for x in range(1, len(bPointDirection)):
            if self.PrintDebug == True:
                print("fntestpointboard(): Testing point: %s" % (x))
            #endif
            bPointDirection[x] = POINT_POSA
            self.fnCommandPoints( x, POINT_POSB)
            self.fnCommandPoints( x, POINT_POSA)
        #endfor
    #endef

    def fntestpowerboard(self):

        for x in range(1, len(bPowerDirection)):
            if self.PrintDebug == True:
                print("fntestpowerboard(): Testing segment: %s" % (x))
            #endif
            self.fnSwitchSegment( x, POWER_FWD)
            self.fnSwitchSegment( x, POWER_REV)
            self.fnSwitchSegment( x, POWER_OFF)
        #endfor
    #endef      

    def fnCommandPoints(self, ThePoint, TheDirection):

        #|**************************************** POINT PATTERNS ***************************************|
	#+-------------------------------+-------------------------------+-------------------------------+
	#|************* A1 **************|************* A2 **************|************* A3 **************| BANK1[bit1,bit2,bit3]
	#+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+
	#|D01|D02|D03|D04|D05|D06|D07|D08|D01|D02|D03|D04|D05|D06|D07|D08|D01|D02|D03|D04|D05|D06|D07|D08| BANK0[bit1,bit2,bit3,bit4,bit5,bit6,bit7,bit8]
	#+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+
	#|P01|P02|P03|P04|P05|P06|P07|P08|P09|P10|P11|P12|P13|P14|P15|P16|P17|P18|P19|P20|P21|P22|P23|P24|
	#+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+
	#
	#Add new logic to set self.pointbank0 and self.pointbank1 to the new values required to drive the point extender based on the value of "ThePoint"
	#"ThePoint" will contain values from 0 to 24, these need to be decoded correctly into "block" and "bit" (0 is to signal "all-off" so can be ignored)
	#self.pointbank0 needs to contain the D1..D8 to drive the "bit"
	#self.pointbank1 needs to contain A1..A3 to select the correct "block"
	#self.pointbank1 already contains 0x80 if POINT_POSA is selected or 0x00 if POINT_POSB is selected, this should not be erased or the point won't fire correctly
	#in order to avoid relay contact arching the ports should be driven as follows:-
	#1] self.pointbank0 to set the "bit" of the "block"
	#2] self.pointbank1 (bit7) to select the position of the point (POINT_POSA or POINT_POSB)
	#3] self.pointbank1 (bit1,bit2,bit3) to fire the point
	#4] self.pointbank0 set to zero and self.pointbank1 set to zero to release and allow the CDU to charge
        
	# clear out previous values
        self.pointbank0 = 0x00

        # Set the relay on IO15 to drive the points through position A, or position B
        if TheDirection == POINT_POSA:
            self.pointbank1 = 0x80
        else:
            self.pointbank1 = 0x00
        #endif

        # Update the internal direction for status reporting
        bPointDirection[ThePoint] = TheDirection

        if (ThePoint >= 1) and (ThePoint <=8):
            self.pointbank0 = PointMask[ThePoint]   # PointMask[] contains the bank0 bitmask the point
            self.pointbank1 = self.pointbank1 + 0x01
        #endif

        if (ThePoint >= 9) and (ThePoint <=16):
            self.pointbank0 = PointMask[ThePoint-8]
            self.pointbank1 = self.pointbank1 + 0x02
        #endif

        if (ThePoint >= 17) and (ThePoint <=24):
            self.pointbank0 = PointMask[ThePoint-16]
            self.pointbank1 = self.pointbank1 + 0x04
        #endif

        if self.PrintDebug == True:
            print("fnCommandPoints(self.pointbank0=0x%02X, self.pointbank1=0x%02X" % (self.pointbank0, self.pointbank1))
        #endif

        # Setup the relay (DIR) first as this takes time to move to the new position
        if TheDirection == POINT_POSA:
            self.fnwriteic2data ( POINT, BANK1, 0x80)
        #endif
        time.sleep(0.01)

        # Sets the relays (bank0) and Darlington (bank1) drvers in the right order to pulse the right point
        self.fnwriteic2data ( POINT, BANK0, self.pointbank0)
        time.sleep(0.01)
        
        self.fnwriteic2data ( POINT, BANK1, self.pointbank1)
        time.sleep(RELAY_DELAY) # Hold the darlington (bank1) closed to allow maximum charge from the CDU to be dumped to the point

        # Switch all outputs off and allow time for the CDU to re-charge, open the dralington (bank1) first to reduce relay arcing
        self.pointbank0 = 0x00
        self.pointbank1 = 0x00
        self.fnwriteic2data ( POINT, BANK1, self.pointbank1)
        self.fnwriteic2data ( POINT, BANK0, self.pointbank0)
        if self.PrintDebug == True:
            print("fnCommandPoints(): Waiting for CDS to recharge %s" % (CDU_RECHARGE_DELAY))
        #endif
        time.sleep(CDU_RECHARGE_DELAY)
        return
    #enddef

    def TogglePoint(self, ThePoint):

        if self.PrintDebug == True:
            print("TogglePoint(%s)" % (ThePoint))
        #endif

        try:

            self.fnCommandPoints(ThePoint, bPointDirection[ThePoint])

            if bPointDirection[ThePoint] == POINT_POSA:
                bPointDirection[ThePoint] = POINT_POSB
            else:
                bPointDirection[ThePoint] = POINT_POSA
            #endif

        except:
            print("TogglePoint(): Error unable to toggle the point!")

        return
    #enddef

    def ToggleSegment(self, TheSegment):

        if self.PrintDebug == True:
            print("ToggleSegment(%s)" % (TheSegment))
        #endif

        try:            

            bPowerDirection[TheSegment] = bPowerDirection[TheSegment] + 1

            if bPowerDirection[TheSegment] > POWER_REV:
                bPowerDirection[TheSegment] = POWER_OFF
            #endif

            self.fnSwitchSegment(TheSegment, bPowerDirection[TheSegment])

        except:
            print("ToggleSegment(): Error unable to toggle the segment!")

        return
    #enddef
  
    def fnSwitchSegment(self, TheSegment, TheDirection):
        # Switch the segment in the required direction

        # Update the internal direction for status reporting
        bPowerDirection[TheSegment] = TheDirection

        # Segment 1 to 4 are on powerbank0
        if (TheSegment >= 1) and (TheSegment <= 4):
            self.powerbank0 = self.fnGenerateBankData( TheSegment, TheDirection, self.powerbank0)
            self.fnwriteic2data ( POWER, BANK0, self.powerbank0)
        #endif

        # Segment 5 to 8 are on powerbank1
        if (TheSegment >= 5) and (TheSegment <= 8):
            self.powerbank1 = self.fnGenerateBankData( TheSegment, TheDirection, self.powerbank1)
            self.fnwriteic2data ( POWER, BANK1, self.powerbank1)
        #endif

        # Short delay to allow relay to settle during POST
        time.sleep(0.01)

        return
    #enddef

    def fnGenerateBankData(self, TheSegment, TheDirection, TheOldBankData):

        # Get the old data that has already been output to the port and strip the bits that will be updated
        TheNewBankData = TheOldBankData & PowerSegmentMask[TheSegment]        

        # Based on the Direction and Segment select a new bitmask then "or" it with the existing bits

        if TheDirection == POWER_OFF:
            TheNewBankData = TheNewBankData + PowerSegmentOff[TheSegment]
        elif TheDirection == POWER_FWD:
            TheNewBankData = TheNewBankData + PowerSegmentFwd[TheSegment]
        elif TheDirection == POWER_REV:
            TheNewBankData = TheNewBankData + PowerSegmentRev[TheSegment]
        else:
            print("fnGenerateBankData(): Invalid Direction")
            TheNewBankData = 0
        #endif                
          
        return TheNewBankData
    #enddef

    def ClearAllPoints(self):
        if self.PrintDebug == True:
            print("ClearAllPoints(): Clear down all outputs")
        #endif
        self.pointbank0 = 0x00
        self.pointbank1 = 0x00
        self.fnwriteic2data( POINT, BANK0, self.pointbank0)
        self.fnwriteic2data( POINT, BANK1, self.pointbank1)

        for x in range(1, len(bPointDirection)):
            bPointDirection[x] = POINT_POSA
        #endfor
        return
    #enddef

    def SwitchOffAllSegments(self):
        if self.PrintDebug == True:
            print("SwitchOffAllSegments(): Clear down all outputs")
        #endif
        self.powerbank0 = 0x00
        self.powerbank1 = 0x00
        self.fnwriteic2data( POWER, BANK0, self.powerbank0)
        self.fnwriteic2data( POWER, BANK1, self.powerbank1)

        for x in range(1, len(bPowerDirection)):
            bPowerDirection[x] = POWER_OFF
        #endfor       

        return
    #enddef

    def GetPointStatus(self, ThePoint):
        return bPointDirection[ThePoint]
    #enddef

    def GetSegmentStatus(self, TheSegment):
        return bPowerDirection[TheSegment]
    #enddef
    
    def __del__(self):
        self.fnresetpowerboard()
        self.fnresetpointboard()        
        return
    #enddef

#endclass

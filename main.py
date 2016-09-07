#!/usr/bin/python
#===================================================================================================================================
# TITLE: I2C TEST PROGRAMME FOR EXTENSION BOARD
# DESCRIPTION: A programe that tests the points/segments connected to the extension
# board using I2C, then provides a graphical and text way to control them
# REVISION: 0.1, 14-Oct-2013, Initial revision
# REVISION: 0.2, 08-Apr-2015, Uses the ExtensionBoard_PointPowerDriver class
# REVISION: 0.3, 12-Apr-2015, Implement power segment and points using keypress, mouse and dynamic variables
# REVISION: 0.4, 24-Dec-2015, Updated point tables to drive up-to 24 points using expander-board
#===================================================================================================================================
#
#===================================================================================================================================
# MY TO DO:
# 1] Load Constants from config file using https://docs.python.org/2/library/configparser.html
#===================================================================================================================================

from pygame import *
import os.path
import sys
import pygame
import time
from ExtensionBoard_PointPowerDriver import ExtensionBoard_PointPowerDriver

REVISION_TEXT = "REVISION: 0.4, 24-Dec-2015, Updated point tables to drive up-to 24 points using expander-board"

# Define the colors we will use in RGB format
OFFA = [127, 127, 127]
FWDA = [  0,   0, 255]
REVA = [255, 255,   0]
OFFB = [127, 127, 127]
FWDB = [  0, 255, 255]
REVB = [255,   0, 255]

Font = None

main_dir = os.path.dirname(sys.argv[0]) # absolute dir name

PointKeycodes = [ord("#"),
    ord("q"), ord("w"), ord("e"), ord("r"), ord("t"), ord("y"), ord("u"), ord("i"), ord("o"), ord("p"),
    ord("a"), ord("s"), ord("d"), ord("f"), ord("g"), ord("h"), ord("j"), ord("k")
]

PowerKeycodes = [ord("0"),
    ord("1"), ord("2"), ord("3"), ord("4"), ord("5"), ord("6"), ord("7"), ord("8")
]

PhyPointHotspots = [[0,0],
    [254, 50], #P01=OK
    [295, 50], #P02=OK
    [255,100], #P03=OK
    [541, 50], #P04=OK
    [500,100], #P05=OK
    [542,100], #P06=OK
    [500,150], #P07=OK                    
    [757, 50], #P08=OK                    
    [950,272], #P09=OK
    [720,500], #P10=OK
    [680,450], #P11=OK
    [460,550], #P12=OK
    [419,500], #P13=OK
    [248,550], #P14=OK
    [521,450], #P15=OK
    [474,401], #P16=OK
    [415,350], #P17=OK
    [310,250], #P18=OK
    [  0,  0], #P19=N/A
    [  0,  0], #P20=N/A
    [  0,  0], #P21=N/A
    [  0,  0], #P22=N/A
    [  0,  0], #P23=N/A
    [  0,  0]  #P24=N/A
]

PointPairHotspots = [0,
     0, #P01=OK
     3, #P02=OK
     2, #P03=OK
     5, #P04=OK
     4, #P05=OK
     7, #P06=OK
     6, #P07=OK                    
     0, #P08=OK                    
     0, #P09=OK
    11, #P10=OK
    10, #P11=OK
    13, #P12=OK
    12, #P13=OK
     0, #P14=OK
     0, #P15=OK
     0, #P16=OK
     0, #P17=OK
     0, #P18=OK
     0, #P19=N/A
     0, #P20=N/A
     0, #P21=N/A
     0, #P22=N/A
     0, #P23=N/A
     0  #P24=N/A
]

PowerHotspots = [[0,0],
                 [664,229,0], [691,229,0], [718,229,0], [745,229,0],
                 [664,311,1], [691,311,1], [718,311,1], [745,311,1]
                ]

SegmentOverlayPoints = [
                [[0,0]], # 0 - OK
                [[734,  50], [938,  50], [950,  62], [950, 538], [940, 550], [780, 550]], #1 - OK
                [[160,  50], [270,  50]], #2 - OK
                [[146,  50], [ 60,  50], [ 50,  63], [ 50, 537], [ 62, 550], [762, 550]], #3 - OK
                [[217, 100], [112, 100], [100, 114], [100, 487], [111, 500], [385, 500]], #4 - OK
                [[233, 100], [890, 100], [900, 112], [900, 485], [890, 500], [400, 500]], #5 - OK
                [[161, 150], [150, 165], [150, 437], [163, 450], [838, 450], [850, 436], [850, 162], [838, 150], [160, 150]], #6 - OK
                [[498, 426], [255, 195]], #7 - OK
                [[282,  50], [717,  50]] #8 - OK
                ]

SegmentOverlayColours = [
                [OFFA, OFFA, OFFA],
                [OFFA, FWDA, REVA],
                [OFFA, FWDA, REVA],
                [OFFA, FWDA, REVA],
                [OFFA, FWDA, REVA],
                [OFFB, FWDB, REVB],
                [OFFB, FWDB, REVB],
                [OFFB, FWDB, REVB],
                [OFFB, FWDB, REVB]
                ]                 

#===============================================================================
# Load an image into a Surface
#===============================================================================
def load_image(thefile):
    # loads an image, prepares it for play
    thefile = os.path.join(main_dir, 'img-data', thefile)
    try:
        surface = pygame.image.load(thefile)
    #endtry
    except pygame.error:
        raise SystemExit('Could not load image "%s" %s' %(thefile, pygame.get_error()))
    #endexcept
    return surface.convert()

#===============================================================================
# The purpose of this function is to paint in the lower section of the screen
# a window of messages.  The function scrolls existing messages up before
# drawing the new message
#===============================================================================
def fndrawhistory(hWnd, thehistory):
    hWnd.blit(Font.render(
        "_____ [COMMAND EVENT HISTORY] ____________________ [Esc=Quit; F1=x1; F2=x2; F3=x3; F9=Linked; F10=POST; 0=Segments off; #=Points off] __________",
        1, (155, 155, 155), (0,0,0)), (2, 600)
    )
    ypos = 680
    h = list(thehistory)
    h.reverse()
    for line in h:
        r = hWnd.blit(line, (0, ypos))
        hWnd.fill(0, (r.right, r.top, 700, r.height))
        ypos -= Font.get_height()
    #endfor
    display.flip()
    return

#===============================================================================
# The purpose of this function is to print a status message to the window
#===============================================================================
def fnprintstatusmessage(message, hWnd, thehistory):
    img = Font.render("%s: %s" % (time.asctime(), message), 1, (50, 200, 50), (0, 0, 0))
    thehistory.append(img)
    fndrawhistory(hWnd, thehistory)    
    return

#===============================================================================
# The purpose of this function is to convert a mouse X,Y into a point and power command
#===============================================================================
def fnconvertmousetokeypress(mousex, mousey):
    thekeycode = 0 # default to invalid

    # Test Physical point hotspots
    for i in range(len(PhyPointHotspots)):
        bytestream = PhyPointHotspots[i]

        if fnTestHotspot(bytestream[0], bytestream[1], mousex, mousey, 10) == True:
            thekeycode = PointKeycodes[i]
            break
        #endif
    #endfor        

    # Test Power hotspots
    for i in range(len(PowerHotspots)):
        bytestream = PowerHotspots[i]

        if fnTestHotspot(bytestream[0], bytestream[1], mousex, mousey, 10) == True:
            thekeycode = PowerKeycodes[i]
            break
        #endif
    #endfor

    return thekeycode
#endef

#===============================================================================
# The purpose of this function is to determine if the mouse click is within the hot spot area
#===============================================================================
def fnTestHotspot(hotspotx, hotspoty, mousex, mousey, tolerance):

    if ((mousex > (hotspotx - tolerance)) and (mousex < (hotspotx + tolerance))):
        if ((mousey > (hotspoty - tolerance)) and (mousey < (hotspoty + tolerance))):
            result = True
        else:
            result = False
        #endif
    else:
        result = False
    #endif 
                   
    return result
#enddef

#===============================================================================
# The purpose of the function is to translate keypresses into point & power actions
#===============================================================================
def fnprocesskeypress(thekeycode):

    try:
        h = list(PointKeycodes)
        thepoint = h.index(thekeycode)
    #endtry
    except:
        thepoint = -1
    #endexcept

    try:
        j = list(PowerKeycodes)
        thepower = j.index(thekeycode)
    #endtry        
    except:
        thepower = -1
    #endexcept        

    return [thepoint, thepower]
#enddef

def fnPainPowerIndicatorStatus(hWnd, hExtensionBoard):
    segment_off_cha = load_image("segment-off-cha.png")
    segment_rev_cha = load_image("segment-rev-cha.png")
    segment_fwd_cha = load_image("segment-fwd-cha.png")

    segment_off_chb = load_image("segment-off-chb.png")
    segment_rev_chb = load_image("segment-rev-chb.png")
    segment_fwd_chb = load_image("segment-fwd-chb.png")    

    for x in range(1,len(PowerHotspots)):

        pos = PowerHotspots[x]
        
        xpos = pos[0] - 13
        ypos = pos[1] - 10
        channel = pos[2]
        
        if (hExtensionBoard.GetSegmentStatus(x) == 0x0):
            if (channel == 0):
                hWnd.blit(segment_off_cha, (xpos, ypos))
            else:
                hWnd.blit(segment_off_chb, (xpos, ypos))
            #endif
                
        #endif

        if (hExtensionBoard.GetSegmentStatus(x) == 0x1):
            if (channel == 0):
                hWnd.blit(segment_fwd_cha, (xpos, ypos))
            else:
                hWnd.blit(segment_fwd_chb, (xpos, ypos))
            #endif
        #endif

        if (hExtensionBoard.GetSegmentStatus(x) == 0x2):
            if (channel == 0):
                hWnd.blit(segment_rev_cha, (xpos, ypos))
            else:
                hWnd.blit(segment_rev_chb, (xpos, ypos))
            #endif                
        #endif
    #endfor    
    return
#enddef

def fnPaintPointStatus(hWnd, hExtensionBoard):
    point_posa = load_image("point-posa.png")
    point_posb = load_image("point-posb.png")

    for x in range(1,len(PhyPointHotspots)):

        # Paint the Physical point hotspots
        pos = PhyPointHotspots[x]

        # Skip if the (x, y) co-ordinates are zero, is will be an un-used point (Physical or Virtual)
        if (pos[0] != 0):
            if (pos[1] != 0):
        
                xpos = pos[0] - 6
                ypos = pos[1] - 6

                if (hExtensionBoard.GetPointStatus(x) == 0x0):
                    hWnd.blit(point_posa, (xpos, ypos))
                #endif

                if (hExtensionBoard.GetPointStatus(x) == 0x1):
                    hWnd.blit(point_posb, (xpos, ypos))
                #endif
            #endif
        #endif             
        
    #endfor    
    return
#enddef

def fnPaintSegmentStatus(hWnd, hExtensionBoard):

    for x in range(1,len(PowerHotspots)):
        pointlist = SegmentOverlayPoints[x]
        colours = SegmentOverlayColours[x]
        pygame.draw.lines(hWnd, colours[hExtensionBoard.GetSegmentStatus(x)], False, pointlist, 6)
    #endfor
    
    return
#enddef

#===============================================================================
# The purpose of the function is to update the screen with latest status
#===============================================================================
def fnUpdateScreenwithStatus(hWnd, hExtensionBoard):
    fnPainPowerIndicatorStatus(hWnd, hExtensionBoard)
    fnPaintSegmentStatus(hWnd, hExtensionBoard)
    fnPaintPointStatus(hWnd, hExtensionBoard)
    return
#enddef

#===============================================================================
# This is the main entry point for the application
#===============================================================================
def main():

    # Init the pygame engine
    print("main(): Starting Graphics Engine")
    pygame.init()

    print("main(): pygame version %s" % pygame.version.ver)

    # Check if pygame supports what we need
    print("main(): Checking pygame capabilities")
    if not pygame.image.get_extended():
        raise SystemExit("main(): Sorry, extended image module required")
    else:
        print("main(): Extended image capability present")
    #endif

    print("main(): Starting up the board")
    ExtensionBoard = ExtensionBoard_PointPowerDriver(0x20, 0x27, False, True)   

    # Set the window size
    print("main(): Switching to Graphics mode")
    win = display.set_mode((1000, 700))
    display.set_caption("BMRC Expansion Board Driver")

    # Set the font sizes
    global Font
    Font = font.Font(None, 20)

    # Load the background
    print("main(): Loading layout background image")
    thebackground = load_image("background.png")
    win.blit(thebackground, (0,0))

    # Purge the command window buffer
    print("main(): Initialisation Complete")
    myhistory = []    

    # Update screen status to initial values
    fnUpdateScreenwithStatus(win, ExtensionBoard)

    # Print out the window title to the status window
    txt, iconname = display.get_caption()
    fnprintstatusmessage(txt, win, myhistory)    

    # Print revision text then enter the main loop
    txt = REVISION_TEXT
    fnprintstatusmessage(txt, win, myhistory)

    # Drive linked points by default (using array PointPairHotspots[] to define which are linked]
    DriveLinkedPoints = True

    # Main application loop
    going = True
    while going:
        for e in event.get():
            if e.type == QUIT:
                going = False
            #endif

            if e.type == KEYDOWN:
                if e.key == K_ESCAPE:
                    going = False
                #endif

                elif e.key == K_F9:

                    DriveLinkedPoints = not DriveLinkedPoints

                    txt = "main(): KeyPress::F9 DriveLinkedPoints=%s" % DriveLinkedPoints
                    fnprintstatusmessage(txt, win, myhistory)
                    myhistory=myhistory[-4:]
                    

                elif e.key == K_F10:
                    txt = "main(): POST"
                    fnprintstatusmessage(txt, win, myhistory)
                    myhistory=myhistory[-4:]
                    
                    ExtensionBoard.POST()
                    fnUpdateScreenwithStatus(win, ExtensionBoard)
        
                    txt = "main(): Ready:"
                    fnprintstatusmessage(txt, win, myhistory)
                    myhistory=myhistory[-4:]
                #endif

                elif e.key == K_F1:

                    ExtensionBoard.ToggleSegment(1)
                    ExtensionBoard.ToggleSegment(2)
                    ExtensionBoard.ToggleSegment(3)
                    ExtensionBoard.ToggleSegment(8)

                    fnUpdateScreenwithStatus(win, ExtensionBoard)

                    txt = "main(): KeyPress::F1 Sequence [S1, S2, S3, S8] toggled"

                    fnprintstatusmessage(txt, win, myhistory)
                    myhistory=myhistory[-4:]                    
                    
                #endif

                elif e.key == K_F2:

                    ExtensionBoard.ToggleSegment(4)
                    ExtensionBoard.ToggleSegment(5)

                    fnUpdateScreenwithStatus(win, ExtensionBoard)

                    txt = "main(): KeyPress::F2 Sequence [S4, S5] toggled"

                    fnprintstatusmessage(txt, win, myhistory)
                    myhistory=myhistory[-4:]                    
                    
                #endif

                elif e.key == K_F3:

                    ExtensionBoard.ToggleSegment(6)

                    fnUpdateScreenwithStatus(win, ExtensionBoard)

                    txt = "main(): KeyPress::F2 Sequence [S6] toggled"

                    fnprintstatusmessage(txt, win, myhistory)
                    myhistory=myhistory[-4:]                    
                    
                #endif

                else:
                    TheKeyCode = e.key
                    ThePointPower = fnprocesskeypress(TheKeyCode)

                    if ThePointPower[0] != -1:
                        if ThePointPower[0] == 0:
                            ExtensionBoard.ClearAllPoints()
                            txt = "main(): KeyPress::Clearing all points"
                        else:
                            # Drive the point (and any pair if needed)
                            ExtensionBoard.TogglePoint(ThePointPower[0])
                            if PointPairHotspots[ThePointPower[0]] != 0 and DriveLinkedPoints == True:
                                ExtensionBoard.TogglePoint(PointPairHotspots[ThePointPower[0]])
                                txt = "main(): KeyPress::Processed point [%s,%s]" % (ThePointPower[0], PointPairHotspots[ThePointPower[0]])
                            else:
                                txt = "main(): KeyPress::Processed point [%s]" % ThePointPower[0]
                            #endif
                                
                            
                        #endif
                        fnUpdateScreenwithStatus(win, ExtensionBoard)
                    #endif

                    if ThePointPower[1] != -1:
                        if ThePointPower[1] == 0:
                            ExtensionBoard.SwitchOffAllSegments()
                            txt = "main(): KeyPress::Clearing all power segments"
                        else:
                            ExtensionBoard.ToggleSegment(ThePointPower[1])
                            txt = "main(): KeyPress::Processed power [%s]" % ThePointPower[1]                                                   
                        #endif
                        fnUpdateScreenwithStatus(win, ExtensionBoard)
                    #endif

                    if ThePointPower[0] == -1 and ThePointPower[1] == -1:
                        txt = "main(): KeyPress::Unknown command [%s]" % TheKeyCode
                    #endif

                    fnprintstatusmessage(txt, win, myhistory)
                    myhistory=myhistory[-4:]
                    
                #endif
                                        
            if e.type == VIDEORESIZE:
                win = display.set_mode(e.size, RESIZABLE)
            #endif

            if e.type == MOUSEBUTTONDOWN and e.button == 1:

                # Get the mouse position and convert to "keypress"
                pos = pygame.mouse.get_pos()
                ThePointPower = fnprocesskeypress(fnconvertmousetokeypress(pos[0], pos[1]))

                if ThePointPower[0] != -1:
                    if ThePointPower[0] == 0:
                        ExtensionBoard.ClearAllPoints()
                        txt = "main(): MouseClick::Clearing all points"
                    else:

                        # Drive the point (and any pair if needed)
                        ExtensionBoard.TogglePoint(ThePointPower[0])
                        if PointPairHotspots[ThePointPower[0]] != 0 and DriveLinkedPoints == True:
                            ExtensionBoard.TogglePoint(PointPairHotspots[ThePointPower[0]])
                            txt = "main(): KeyPress::Processed point [%s,%s]" % (ThePointPower[0], PointPairHotspots[ThePointPower[0]])
                        else:
                            txt = "main(): KeyPress::Processed point [%s]" % ThePointPower[0]
                        #endif
                                
                    #endif
                    fnUpdateScreenwithStatus(win, ExtensionBoard)
                #endif

                if ThePointPower[1] != -1:
                    if ThePointPower[1] == 0:
                        ExtensionBoard.SwitchOffAllSegments()
                        txt = "main(): MouseClick::Clearing all power segments"
                    else:                    
                        ExtensionBoard.ToggleSegment(ThePointPower[1])
                        txt = "main(): MouseClick::Processed power [%s]" % ThePointPower[1]
                    #endif
                    fnUpdateScreenwithStatus(win, ExtensionBoard)
                #endif

                if ThePointPower[0] == -1 and ThePointPower[1] == -1:
                    txt = "main(): MouseClick::Unknown command!"
                #endif
                    
                fnprintstatusmessage(txt, win, myhistory)
                myhistory=myhistory[-4:]
            #endif
        #endfor
                     
        time.sleep(0.1)
    #endwhile

    txt = "main(): Shutdown"
    fnprintstatusmessage(txt, win, myhistory)
    myhistory=myhistory[-4:]

    # Clear all points to allow the CDU to reset, then exit
    print("main(): Cleaning up")
    pygame.quit()
    return

#===============================================================================
# Set the entry point for the application
#===============================================================================
if __name__ == '__main__':
    main()
#endif    

#EOF

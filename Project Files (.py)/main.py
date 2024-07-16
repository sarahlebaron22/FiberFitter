import numpy as np
import time
from pylablib.devices import Newport ## for Picomotor 8742
from labjack import ljm ## for LabJack T7

""" Goals:
    1.) Design a modular gradient ascent algorithm with variable delta/epsilon

    2.) Have gradient calculations be determined by number of detected motorized axes
        - Will need to store number of motor slots in use and which motor slots are in use
    3.) Design a tracking database/system/thing for current fiber coupling efficiency
        - Each system will have their own individual fiber coupling efficiency reading. Need to have each independent instance of system
          feed back to a centralized unit with this variable and compile it into a database that keeps track of which coupling is being referenced
    4.) Design a modular movement algorithm for mirror mounts that uses data from gradient ascent algorithm

    How data will be fed/read/acted on:
    tracking system --> gradient ascent algorithm --> movement algorithm then repeat, stop.
        - data from tracking system will be used as a reference for f(x,y,z,w) in gradient ascent algo. Then algo will call for a movement of delta,
          then tracking system will detect change in efficiency from movement, which will be fed back into ascent algorithm to find gradient, which
          will finally be fed into movement algorithm for the "final" movement for a single instance of the auto-aligner. Rinse and repeat as many
          time as possible.

"""

## necessary globals. Sorry about that. All of these should be constants, and all will be denoted with capslock
global PICOMOTOR, LABJACK

def initializePicomotorUSB(): ## Used to detect Picomotor through a USB connection. Will talk with the Picomotor.
                              ## At some point, may want to change this to just "initializePicomotor" and have it attempt both USB and ethernet access
    try:
        PICOMOTOR = Newport.Picomotor8742()
        PICOMOTOR.set_position_reference(axis=1)
        PICOMOTOR.set_position_reference(axis=2)
        PICOMOTOR.set_position_reference(axis=3)
        PICOMOTOR.set_position_reference(axis=4) ## sets current coordinates of motors to [0,0,0,0]
    except Exception as error:
        print(f"Device not connectable. Reason: {error}")



def locateAxes(): ## Used to determine number of independent mirror mounts. Will talk with Picomotor.
    try:
        axesInUse = PICOMOTOR.get_all_axes()
        return len(axesInUse)
    except Exception as error:
        print(f"Cannot detect axis. Has the Picomotor been initialized? \n Reason: {error}")



def initializeLabjack(): ## Will talk with LabJack
    try:
        LABJACK = ljm.openS("ANY","ANY","ANY") ## Opens the first Labjack found in the system
    except Exception as error:
        print(f"Could not open the LabJack. Reason: {error}")



def getFiberEfficiency(preCoupleName, postCoupleName): ## Will talk with the LabJack
                                                       ## "name" refers to which port on the LabJack each piece of data is being fed into
                                                       ## i.e.:AIN0, AIN1, etc.
    try: 
        preCoupleReading = ljm.eReadName(LABJACK, preCoupleName)
        postCoupleReading = ljm.eReadName(LABJACK, postCoupleName)
        efficiencyReading = postCoupleReading/preCoupleReading
        return efficiencyReading 
    except Exception as error:
        print(f"Had issues collecting fiber coupling efficiency. Reason: {error}")


def gradientAscent(delta, epsilon, axes, cutoff, preCoupleName, postCoupleName):
    ##steps to ascend
    ## 1.) Document current efficiency coupling. Store as f(x). Requires call to LabJack.
    ## 2.) Increment by delta. Requires call to Picomotor
    ## 3.) Document new efficiency coupling. Store as f(x + delta). Requires call to LabJack
    ## 4.) Calculate gradient on all axes as df = [f(x + delta) - f(x)]/delta.
    ## 5.) return df*epsilon
    ## 6.) (Optional; should I make another function for this?) Have Picomotor move to its original location plus df*epsilon. Requires call to Picomotor.

    efficiencyOld = getFiberEfficiency(preCoupleName, postCoupleName) ## Reads from LabJack
    motorLocation = [PICOMOTOR.get_position(axis=1), PICOMOTOR.get_position(axis=2), 
                     PICOMOTOR.get_position(axis=3), PICOMOTOR.get_position(axis=4)]
    
    movementGradient = [] ## is a list instead of an integer because it will document changes in efficiency from movement in each direction 

    for i in range (0, axes):
        PICOMOTOR.move_by(axis=i+1, steps=delta)
        changeInEfficiency = getFiberEfficiency(preCoupleName, postCoupleName)
        movementGradient.append[(changeInEfficiency - efficiencyOld)/delta]
        PICOMOTOR.move_to(axis=i+1, position=motorLocation[i]) ##brings mirror back to reference location

    for i in range (0, axes):
        if motorLocation[i]+(movementGradient*epsilon) > cutoff:
            PICOMOTOR.move_to(axis=i+1, position=cutoff)
        elif motorLocation[i]+(movementGradient*epsilon) < -cutoff:
            PICOMOTOR.move_to(axis=i+1, position=cutoff)  
        else:        
            PICOMOTOR.move_to(axis=i+1, position=motorLocation[i]+(movementGradient[i]*epsilon))

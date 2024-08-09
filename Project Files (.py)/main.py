import numpy as np
import time
from pylablib.devices import Newport ## for Picomotor 8742
from labjack import ljm ## for LabJack T7
from sklearn.linear_model import SGDRegressor
import csv
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

def initializePicomotorUSB(): ## Used to detect Picomotor through a USB connection. Will talk with the Picomotor.
                              ## At some point, may want to change this to just "initializePicomotor" and have it attempt both USB and ethernet access
    try:
        global PICOMOTOR
        PICOMOTOR = Newport.Picomotor8742()
        PICOMOTOR.set_position_reference(axis=1)
        PICOMOTOR.set_position_reference(axis=2)
        PICOMOTOR.set_position_reference(axis=3)
        PICOMOTOR.set_position_reference(axis=4) ## sets current coordinates of motors to [0,0,0,0]
    except Exception as error:
        print(f"Device not connectable. Reason: {error}")



def locateAxes(PICOMOTOR): ## Used to determine number of independent mirror mounts. Will talk with Picomotor.
    try:
        axesInUse = PICOMOTOR.get_all_axes()
        return len(axesInUse)
    except Exception as error:
        print(f"Cannot detect axis. Has the Picomotor been initialized? \n Reason: {error}")



def initializeLabjack(): ## Will talk with LabJack
    try:
        LABJACK = ljm.openS("ANY","ANY","ANY") ## Opens the first Labjack found in the system
        print("LabJack connected. Ready to play.")
    except Exception as error:
        print(f"Could not open the LabJack. Reason: {error}")



def getFiberEfficiency(LABJACK, preCoupleName, postCoupleName): ## Will talk with the LabJack
                                                       ## "name" refers to which port on the LabJack each piece of data is being fed into
                                                       ## i.e.:AIN0, AIN1, etc.
    try: 
        preCoupleReading = ljm.eReadName(LABJACK, preCoupleName)
        postCoupleReading = ljm.eReadName(LABJACK, postCoupleName)
        efficiencyReading = (postCoupleReading*2/0.9)/(preCoupleReading/0.05) ## *2 accounts for terminator difference, /0.9 and /0.05 account for ratio of beamsplitter
        return efficiencyReading 
    except Exception as error:
        print(f"Had issues collecting fiber coupling efficiency. Reason: {error}")



##note: a failure
def newGradientAscent(labjack, picomotor, preCoupleName, postCoupleName, delta, epsilon, cutoff, axes, goal):
    ## labjack = your labjack is named once opened, picomotor = your named picomotor once opened
    ## preCoupleName = name of ain used to measure pre-couple laser power, postCoupleName = ain for post-couple laser power
    ## delta = number of initial steps taken to search gradient, epsilon = final multiplier to gradient to determine step size
    ## range = maximum number of allowed net steps in any given direction (hopefully to prevent veering outside the couple entirely)
    ## axes = number of motorized axes (for a particular system, should be b/t 1-4)
    ## goal = goal efficiency to be reached. Width of steps will decrease as script approaches goal to prevent overshoot

    efficiencyOld = getFiberEfficiency(labjack, preCoupleName, postCoupleName)
    overshootMinimizer = (goal - efficiencyOld)
    position = [picomotor.get_position(axis=1), picomotor.get_position(axis=2), 
                picomotor.get_position(axis=3), picomotor.get_position(axis=4)]
    
    d = []
    for i in range(0, axes):
        ## This will be the 'scouting step', where algorithm prompts picomotor to move by the delta, record new efficiency, and 
        ## calculate the gradient based off of it before returning to origin
        picomotor.move_by(axis=i+1, steps=delta)
        time.sleep(1.5)
 
        newEfficiency = getFiberEfficiency(labjack, preCoupleName, postCoupleName)
        d.append((newEfficiency - efficiencyOld)/delta)
        picomotor.move_by(axis=i+1, steps=-delta) ##want to move back to origin but accounting for backwards steps being a bit larger
        time.sleep(1)

    for i in range(0, axes):
        newLocation=round(position[i]+d[i]*epsilon*overshootMinimizer)
        if newLocation >= cutoff:
            newLocation=cutoff
        elif newLocation <= -cutoff:
            newLocation=-cutoff
        else:
            continue
        picomotor.move_to(axis=i+1, position=newLocation)
        time.sleep(1.5)
        position[i]=picomotor.get_position(axis=i+1)

def manualBeamWalkAlgo(labjack, picomotor, preCoupleName, postCoupleName, stepsize, axes):
    '''steps in walking the beam:
    1.) move knob one direction
        - if efficiency goes up, keep moving that direction
        - if not, try other direction
            - if efficiency goes up, move in other direction
            - if not, STOP
    2.) move on other axis. Repeat steps.
    3.) Repeat 1 and 2 until optimum reached
    '''
    efficiencyOld = getFiberEfficiency(labjack, preCoupleName, postCoupleName)
    for i in range(0,axes):
        picomotor.move_by(axis=i+1, steps=stepsize)
        time.sleep(0.5)
        efficiencyNew = getFiberEfficiency(labjack, preCoupleName, postCoupleName)
        if efficiencyNew<efficiencyOld:
            picomotor.move_by(axis=i+1, steps=-2*stepsize)
            time.sleep(0.5)
            efficiencyNew = getFiberEfficiency(labjack, preCoupleName, postCoupleName)
            if efficiencyNew<efficiencyOld:
                picomotor.move_by(axis=i+1, steps=stepsize)
                time.sleep(0.5)
 
def curveFitter(labjack, picomotor, preCoupleName, postCoupleName, randPoints, axes, csvFile):
    '''
     hoping this one is the one -- doesn't require knowledge of function and prioritizes a minimal dataset, which
     is important bc of the picomotor movement imprecision. Too much data collection can result in earlier datapoints
     being completely unreliable.
     
     Steps: 1.) Take a few random points within a bound
            2.) 
    '''
                   
    randomCoords=[]
    randomEfficiencies=[]
    

    for i in range(0, axes):
        for j in range(0, randPoints):
            picomotor.move_by(axis=i+1, steps=np.random.randint(-4, 4))
            time.sleep(0.3)
            randomCoords.append(picomotor.get_position(axis=i+1))
            randomEfficiencies.append(-(getFiberEfficiency(LABJACK=labjack, preCoupleName=preCoupleName, postCoupleName=postCoupleName)))
        regressor=SGDRegressor()
        regressor.fit(np.reshape(randomCoords, (-1, 1)), randomEfficiencies)
        
    
        historicEfficiencies=[]
        historicLocationX=[]
        historicLocationY=[]

        with open(f"{csvFile}.csv", 'r', newline='') as csvefficiency:
            csvreader = csv.reader(csvefficiency)
            next(csvreader, None)
            next(csvreader, None)
            for row in csvreader:
                historicEfficiencies.append(float(row[0]))
                historicLocationX.append(int(row[17]))
                historicLocationY.append(int(row[18]))
        
        while len(historicEfficiencies) > 200:
            del historicEfficiencies[0]
            del historicLocationX[0]
            del historicLocationY[0]
            
        
        lowestPoint=1
        placeNow=picomotor.get_position(axis=i+1)
        for k in range(placeNow-6, placeNow+6):
            newLowestPoint=regressor.predict(np.reshape([k], (1, -1)))
            if newLowestPoint<lowestPoint:
                lowestPoint=newLowestPoint
                optimalCoord=k
            else:
                optimalCoord=picomotor.get_position(axis=i+1)
        picomotor.move_to(axis=i+1, position=optimalCoord)
        time.sleep(0.2)
        
        currentBest = max(historicEfficiencies)
        if currentBest > (getFiberEfficiency(LABJACK=labjack, preCoupleName=preCoupleName, postCoupleName=postCoupleName)+0.125):
            bestEfficiency = historicEfficiencies.index(currentBest)
            bestLocationX = historicLocationX[bestEfficiency]
            bestLocationY = historicLocationY[bestEfficiency]
            picomotor.move_to(axis=1, position=bestLocationX)
            time.sleep(0.1)
            picomotor.move_to(axis=2, position=bestLocationY)
            print(f"went too far, attempting recovery")
        else:
            pass
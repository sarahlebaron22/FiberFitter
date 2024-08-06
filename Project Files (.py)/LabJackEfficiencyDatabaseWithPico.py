
import main
import threading
from pylablib.devices import Newport
from tkinter import *
from tkinter import ttk
from tkinter import simpledialog
from labjack import ljm
import csv
import time
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

##How to collect LabJack data and send it to frame
##1.) Ask user how many fiber coupled systems there are
##2.) Prompt user to input names of two analog inputs for each coupled system


def getCoupledSystems():
    global coupledSystems
    global allCoupledSystemNames
    coupledSystems =simpledialog.askinteger('LabJack Initialization', "How many coupled systems are currently being tracked by the LabJack?")
    allCoupledSystemNames=[[0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0]]
    for i in range(0, coupledSystems):
        preFiberCouple = simpledialog.askstring('Pre-Couple Address Info', f"Type the name of the analog input corresponding to system {i+1}'s pre-couple photodetector reading (i.e.: A1N0, A1N5, etc.)")
        postFiberCouple = simpledialog.askstring('Post-Couple Address Info', f"Type the name of the analog input corresponding to system {i+1}'s post-couple photodiode (i.e.: A1N0, A1N5, etc.)")
        allCoupledSystemNames[i]=[preFiberCouple, postFiberCouple]
    

## This will give us all the fiber coupled systems we want to display and which addresses correspond to the photodetectors used to calculate
## efficiency. From here, we just get the labjack to read from each address, do the basic getFiberEfficiency() stuff, and feed that into our
## GUI.



def writeToDisk(entries):
    with open(f"{csvEfficiency}.csv", "a", newline='') as csvefficiency:
        csvwriterE=csv.writer(csvefficiency)
        csvwriterE.writerow(entries)

        
def refreshFiberEfficiencies():
    global newEntries   
    newEntries = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0] ##idk why this needed a new list to work, but when I tried just pulling from allFiberEfficiencies, it wouldn't refresh on the csv file
    try:
        for i in range (0, coupledSystems):
            newEntries[i]=(round(main.getFiberEfficiency(LABJACK, allCoupledSystemNames[i][0], allCoupledSystemNames[i][1]), 3))

    except:
        pass
    totalTimeRan = round(time.time() - start, 3)
    newEntries[16]=totalTimeRan
    try:
        picoPosition = stage.get_position()
        newEntries[17]=picoPosition[0]
        newEntries[18]=picoPosition[1]
    except:
        pass


##adding capacity for making a graph at any point in time:

    
## now we make the actual plot part


def timePlot(groupMonitored, imageName): 
    x=[]
    y=[]
    with open(f"{csvEfficiency}.csv", 'r', newline='') as csvefficiency:
        csvreaderE=csv.reader(csvefficiency)
        for row in csvreaderE:
            if row == None:
                continue
            else:
                x.append(float(row[16]))
                y.append(float(row[groupMonitored-1]))

    ax = plt.subplot()
    ax.plot(x, y)
    ax.set(xlabel='Time', ylabel='Efficiency', title=f'Efficiency of Group {groupMonitored}')
    plt.savefig(f'{imageName}.png')
    time.sleep(0.5)
    img=Image.open(f'{imageName}.png')
    img.show()
    ax.cla()
    x.clear()
    y.clear()



def stepsPlot(groupNumber, imageName): 
    x=[]
    y=[]
    z=[]
    with open(f"{csvEfficiency}.csv", 'r', newline='') as csvefficiency:
        csvreaderE=csv.reader(csvefficiency)
        for row in csvreaderE:
            if row == None:
                continue
            else:
                x.append(float(row[17]))
                y.append(float(row[18]))
                z.append(float(row[groupNumber-1]))

    ax = plt.subplot(projection='3d')
    ax.scatter(x, y, z)
    ax.set(xlabel='x steps', ylabel='y steps', title=f'Efficiency of Group {groupNumber}')
    plt.savefig(f'{imageName}.png')
    time.sleep(0.5)
    img=Image.open(f'{imageName}.png')
    img.show()
    ax.cla()
    x.clear()
    y.clear()
    z.clear()

def getTimeGraph():
    group = simpledialog.askinteger("", "what group do you want to graph? (insert group number ONLY)")
    iname = simpledialog.askstring("", "give an image file name")
    timePlot(group, iname)
    
def getStepsGraph():
    group = simpledialog.askinteger("", "what group do you want to graph? (insert group number ONLY)")
    iname = simpledialog.askstring("", "give an image file name")
    stepsPlot(group, iname)


def updateGrid(refreshRate=500):
    refreshFiberEfficiencies()
    writeToDisk(newEntries)
    for i in range (0, coupledSystems):
        exec(f"couple{i+1}.config(text=newEntries[{i}])") ## okay fine I used an exec() bite me
    for i in range (coupledSystems, 16):
        exec(f"couple{i+1}.config(text='Not in Use')") ## okay fine I used an exec() bite me

        ##saveData()
    if running:
        window.after(refreshRate, updateGrid) ## updates panel every second


def renameFunctionality():
    groupNum = simpledialog.askinteger("", "Which fiber group do you want to rename?")
    newName = simpledialog.askstring("", f"Give a new name for group {groupNum}")
    exec(f"frame{groupNum}.configure(text='{newName} {groupNum}')")

def buttonFunctionality():
    running = False
    getCoupledSystems()
    running = True


## now we make the frame
root = Tk()
root.title("Fibercouple Database")

window = ttk.Frame(root, padding='0.5i')

frame = ttk.Frame(root)
window.grid(column=0, row=0, sticky='NSEW')


## now we set up the frame such that all of this data gets fed into the correct number of collumns
## to start out, I'll construct a database of 16 columns for 16 fiber coupled systems. Idk if we'll ever
## exceed that.


frame1 = ttk.LabelFrame(window, text="Group 1")
frame1.grid(column=0, row=0, sticky='NSWE')
couple1 = ttk.Label(frame1, borderwidth=1, font=15)
couple1.grid(column=0, row=0, sticky='NSWE')

frame2 = ttk.LabelFrame(window, text="Group 2")
frame2.grid(column=1, row=0,sticky='NSWE')
couple2 = ttk.Label(frame2, borderwidth=1, font=15)
couple2.grid(column=1, row=0, sticky='NSWE')


frame3 = ttk.LabelFrame(window, text="Group 3")
frame3.grid(column=2, row=0, sticky='NSWE')
couple3 = ttk.Label(frame3, borderwidth=1, font=15)
couple3.grid(column=2, row=0, sticky='NSWE')


frame4 = ttk.LabelFrame(window, text="Group 4")
frame4.grid(column=3, row=0, sticky='NSWE')
couple4 = ttk.Label(frame4, borderwidth=1, font=15)
couple4.grid(column=3, row=0, sticky='NSWE')


frame5 = ttk.LabelFrame(window, text="Group 5")
frame5.grid(column=0, row=1, sticky='NSWE')
couple5 = ttk.Label(frame5, borderwidth=1, font=15)
couple5.grid(column=0, row=1, sticky='NSWE')


frame6 = ttk.LabelFrame(window, text="Group 6")
frame6.grid(column=1, row=1, sticky='NSWE')
couple6 = ttk.Label(frame6, borderwidth=1, font=15)
couple6.grid(column=1, row=1, sticky='NSWE')


frame7 = ttk.LabelFrame(window, text="Group 7")
frame7.grid(column=2, row=1, sticky='NSWE')
couple7 = ttk.Label(frame7, borderwidth=1, font=15)
couple7.grid(column=2, row=1, sticky='NSWE')


frame8 = ttk.LabelFrame(window, text="Group 8")
frame8.grid(column=3, row=1, sticky='NSWE')
couple8 = ttk.Label(frame8, borderwidth=1, font=15)
couple8.grid(column=3, row=1, sticky='NSWE')


frame9 = ttk.LabelFrame(window, text="Group 9")
frame9.grid(column=0, row=2, sticky='NSWE')
couple9 = ttk.Label(frame9, borderwidth=1, font=15)
couple9.grid(column=0, row=2, sticky='NSWE')


frame10 = ttk.LabelFrame(window, text="Group 10")
frame10.grid(column=1, row=2, sticky='NSWE')
couple10 = ttk.Label(frame10, borderwidth=1, font=15)
couple10.grid(column=1, row=2, sticky='NSWE')


frame11 = ttk.LabelFrame(window, text="Group 11")
frame11.grid(column=2, row=2, sticky='NSWE')
couple11 = ttk.Label(frame11, borderwidth=1, font=15)
couple11.grid(column=2, row=2, sticky='NSWE')


frame12 = ttk.LabelFrame(window, text="Group 12")
frame12.grid(column=3, row=2, sticky='NSWE')
couple12 = ttk.Label(frame12, borderwidth=1, font=15)
couple12.grid(column=3, row=2, sticky='NSWE')


frame13 = ttk.LabelFrame(window, text="Group 13")
frame13.grid(column=0, row=3, sticky='NSWE')
couple13 = ttk.Label(frame13, borderwidth=1, font=15)
couple13.grid(column=0, row=3, sticky='NSWE')


frame14 = ttk.LabelFrame(window, text="Group 14")
frame14.grid(column=1, row=3, sticky='NSWE')
couple14 = ttk.Label(frame14, borderwidth=1, font=15)
couple14.grid(column=1, row=3, sticky='NSWE')


frame15 = ttk.LabelFrame(window, text="Group 15")
frame15.grid(column=2, row=3, sticky='NSWE')
couple15 = ttk.Label(frame15, borderwidth=1, font=15)
couple15.grid(column=2, row=3, sticky='NSWE')


frame16 = ttk.LabelFrame(window, text="Group 16")
frame16.grid(column=3, row=3, sticky='NSWE')
couple16 = ttk.Label(frame16, borderwidth=1, font=15)
couple16.grid(column=3, row=3, sticky='NSWE')


## Yes this is ugly and convoluted. No there is not a better option, unless I want to make a for loop of exec() functions 
## ala exec(f"couple{i} = ...")
## if fewer than 16 systems are couples, those spaces will simplybe left blank

## This command tells all labjack inputs to designate their voltage range from -0.01 to 0.01 volts.
## Since max readings will likely be in the ballpart of 0.07-0.08. If it peaks out above that, adjust "value" to = 0.1. We want the narrowest range possible for the most precision, but technically it can go up to value = 10.

LABJACK = ljm.openS("ANY", "ANY", "ANY")
ljm.eWriteAddress(handle=LABJACK, address=43900, dataType=ljm.constants.FLOAT32, value=1) 


## Adding a button to refresh if new labjacks are inserted
refreshButton = ttk.Button(window, text="New Coupling", command=buttonFunctionality)
refreshButton.grid(row=4, columnspan=2, sticky='NSEW')


## Adding another button for graphing capacity
graphButton = ttk.Button(window, text="Plot Time", command=getTimeGraph)
graphButton.grid(row=4, column=2, sticky='NSEW')

graphButton2 = ttk.Button(window, text="Plot Steps", command=getStepsGraph)
graphButton2.grid(row=5, column=3, sticky='NSEW')

## By Sam's suggestion, adding another button for renaming groups.
## By Vandy's suggestion, preserving group number during renaming.
renameButton = ttk.Button(window, text="Rename group", command=renameFunctionality)
renameButton.grid(row=4, column=3, sticky='NSEW')



def ascentButtonCommand():
    main.manualBeamWalkAlgo(labjack=LABJACK, picomotor=stage, preCoupleName='ain0', postCoupleName='ain1', 
                           stepsize=2, axes=2)

def threadedButtonCommand(): ##necessary to thread, or else CSV file wont be written to and GUI won't be refreshed while running
    t=threading.Thread(target=ascentButtonCommand, args=())
    t.start()   
    
ascentButton = ttk.Button(window, text="Ascent (TEST)", command=threadedButtonCommand)
ascentButton.grid(row=5, columnspan=3, sticky='NSEW')


## initializing the GUI
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

window.columnconfigure(0, weight=1)
window.columnconfigure(1, weight=1)
window.columnconfigure(2, weight=1)
window.columnconfigure(3, weight=1)
window.columnconfigure(4, weight=1)

window.rowconfigure(0, weight=1)
window.rowconfigure(1, weight=1)
window.rowconfigure(2, weight=1)
window.rowconfigure(3, weight=1)
window.rowconfigure(4, weight=1)



## running the program
running = True
counter = 0


## making the csv file for data storage
csvEfficiency = simpledialog.askstring('CSV file creation', "Create a name for the CSV file the coupling data will be written to")


##with open(f"{csvEfficiency}.csv", "w") as csvefficiency:
##    csvwriterE=csv.writer(csvefficiency)
##    csvwriterE.writerow(['Group 1', 'Group 2', 'Group 3', 'Group 4', 'Group 5', 'Group 6', 'Group 7', 
##                         'Group 8', 'Group 9', 'Group 10', 'Group 11', 'Group 12', 'Group 13', 'Group 14', 
##                         'Group 15', 'Group 16', 'Time', 'x-steps', 'y-steps'])
    
try: ##Doing a "try" thing here in case you wanna run the Database w/o Picomotor support
    stage=Newport.Picomotor8742()

except:
    ascentButton.config(state=DISABLED)
    pass

start=time.time()

getCoupledSystems()
updateGrid(500)
root.minsize(height=300, width=700)
root.mainloop()



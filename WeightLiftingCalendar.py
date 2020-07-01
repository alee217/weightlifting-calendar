"""
TODO:
4. Make sure everything scales right
5. Add paddings
7. Fix any text not fitting in any entries or labels
"""

from tkinter import *
from tkinter import ttk
from tkinter import font
import os
import webbrowser
from datetime import date

class Timer:
    # Must grid it yourself
    def __init__(self, container):
        self.container = container
        timerFont = font.Font(family='Arial', size=42, weight='bold')
        self.timer = ttk.Label(container, width=5, anchor=CENTER, text="00:00", background='#ffffff', relief='groove', font=timerFont)
        self.startClicked = False
        self.resetClicked = False
    
    def start(self):
        if not self.startClicked:
            self.startClicked = True
            root.after(1000, self.updateTimer)

    def reset(self):
        self.startClicked = False
        self.resetClicked = True
        self.timer.configure(text=str('00:00'))

    def updateTimer(self):
        if self.resetClicked:
            self.resetClicked = False
            return
        min, sec = self.timer['text'].split(':')
        sec = int(sec) + 1
        if sec == 60:
            min = int(min)
            sec = '00'
            min += 1
            if min < 10:
                min = '0' + str(min)
            elif min == 60:
                min = '00'
            else:
                min = str(min)
        else:
            if sec < 10:
                sec = '0' + str(sec)
            else:
                sec = str(sec)
        self.timer.configure(text = min + ":" + sec)
        root.after(1000, self.updateTimer)

class ScrollFrame:
    def __init__(self, container):
        self.canvas = Canvas(container, highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient=VERTICAL, command=self.canvas.yview)
        self.scrollFrame = ttk.Frame(self.canvas)
        self.scrollFrame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )
        self.canvas.create_window((0, 0), window=self.scrollFrame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.pack()
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.scrollFrame.bind('<Enter>', self.boundMouseWheel)
        self.scrollFrame.bind('<Leave>', self.unboundMouseWheel)

    def boundMouseWheel(self, event):
        self.canvas.bind_all("<MouseWheel>", self.onMouseWheel)   
        
    def unboundMouseWheel(self, event):
        self.canvas.unbind_all("<MouseWheel>") 

    def onMouseWheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")       

EXCER_WIDTH = 44 # Width of each exercise label
SR_WIDTH = 13 # Width of each sets and reps label
HEAD_COLOR = '#005599' # Color of the header background
HEAD_LETTER = '#FFFFFF' # Color of the header text

root = Tk()
root.title("Calendar")
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

# Font for the displayed exercise info
excerFont = font.Font(family='Arial', size=13)

# Font for the excercise header
headFont = font.Font(family='Arial', size=13, weight='bold')

# Font for the day
dayFont = font.Font(family='Arial', size=16, weight='bold')

# Font for the counter
countFont = font.Font(family='Arial', size=72, weight='bold')

daysSuggestion = ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday')

dayFrames = None
dayOfWeekList = None
workoutTypes = None
dayLabels = None
dayButtons = None
dayFrameToWorkFrames = None
dayFrameToWorkLabels = None
dayFrameToWorkButtons = None
dayFrameToWorkouts = None
scrollFrame = None
confirmButton = None
displayFrame = None
count = None
countTimeFrame = None

def init():
    global dayFrames, dayOfWeekList, workoutTypes, dayLabels, dayButtons, dayFrameToWorkFrames, dayFrameToWorkLabels, dayFrameToWorkButtons, dayFrameToWorkouts
    dayFrames = []  # list of frames containing everything for each day
    dayOfWeekList = []  # list of all the user's selected day of week for each day
    workoutTypes = []   # workout description for each day
    dayLabels = []  # list of the labels that numbers each day
    dayButtons = []  # list of add buttons for each day.
    dayFrameToWorkFrames = {}  # dict from dayFrame to list of workFrames that contains everything for each workout.
    dayFrameToWorkLabels = {}  # dict from dayFrame to list of workLabels that numbers each workout
    dayFrameToWorkButtons = {}  # dict from dayFrame to list of workButtons that adds new workout
    dayFrameToWorkouts = {}  # dict from dayFrame to list of workout info.

def new():
    global scrollFrame

    init()
    top = Toplevel()
    top.title('New')
    top.columnconfigure(0, weight=1)
    top.rowconfigure(0, weight=1)
    top.grab_set()
    top.minsize(1060, 500)

    container = ttk.Frame(top, borderwidth=5, relief='solid')
    container.grid(row=0, padx=5, pady=5, sticky=(N, E, S, W))

    scrollFrame = ScrollFrame(container).scrollFrame

    frame = ttk.Frame(scrollFrame)
    frame.grid()
    ttk.Button(frame, text="Add Day", command=lambda arg = -1: addDay(arg)).grid(column=0, row=0)
    dayFrames.append(frame)
    confirmButton = ttk.Button(top, text="Confrim", command=writeToFile)
    confirmButton.grid(pady=5)

def addDay(dayNum):
    if dayNum == -1:
        frame = dayFrames.pop()
        frame.destroy()
        dayNum += 1

    dayFrame = ttk.Frame(scrollFrame)
    dayFrame.grid(row=dayNum, sticky=(N, W, E, S))    
    dayFrames.insert(dayNum, dayFrame)

    dayHeaderFrame = ttk.Frame(dayFrame)
    dayHeaderFrame.grid(column=0, row=0, sticky=(N, W, E, S))

    day = StringVar()
    dayOfWeekList.insert(dayNum, day)

    dayLabel = ttk.Label(dayHeaderFrame, text='Day ' + str(dayNum+1) + ' : ')
    dayLabel.grid(column=0, row=0)
    dayLabels.insert(dayNum, dayLabel)
    dayCombo = ttk.Combobox(dayHeaderFrame, width=11, textvariable=day)
    dayCombo['values'] = daysSuggestion
    dayCombo.current(0)
    dayCombo.grid(column=1, row=0)

    type = StringVar()
    workoutTypes.insert(dayNum, type)
    ttk.Entry(dayHeaderFrame, width=45, textvariable=type).grid(column=2, row=0)

    workFrame = ttk.Frame(dayFrame)
    workFrame.grid(row=1, sticky=(N, W, E, S))
    dayFrameToWorkFrames[dayFrame] = [workFrame]

    ttk.Label(workFrame, text="Add workout...").grid(column=0, row=0)
    ttk.Button(workFrame, width=3, text="+", command=lambda curr1 = dayFrame, curr2 = -1: addWorkout(curr1, curr2)).grid(column=1, row=0)

    addButton = ttk.Button(dayFrame, text="Add Day", command=lambda arg = dayNum+1: addDay(arg))
    addButton.grid(column=0, row=2)
    ttk.Button(dayHeaderFrame, text="Remove Day", command=lambda curr = dayFrame: removeDay(curr)).grid(column=3, row=0)

    dayButtons.insert(dayNum, addButton)
    for currDay in range(dayNum+1, len(dayFrames)):
        dayFrames[currDay].grid(row=currDay, sticky=(N, W, E, S))
        dayLabels[currDay]['text'] = 'Day ' + str(currDay+1) + ' : '
        dayButtons[currDay]['command'] = lambda arg = currDay: addDay(arg)
        #dayButtons[currDay]['text'] = "Add Day " + str(currDay)
    #confirmButton.grid(row=confirmButton.grid_info()['row']+1, sticky=E)

def removeDay(dayFrame):
    try:
        dayNum = dayFrames.index(dayFrame)
    except ValueError:
        return
    dayOfWeekList.pop(dayNum)
    workoutTypes.pop(dayNum)
    dayLabels.pop(dayNum)
    dayButtons.pop(dayNum)
    dayFrameToWorkFrames.pop(dayFrame)
    try:
        dayFrameToWorkButtons.pop(dayFrame)
        dayFrameToWorkLabels.pop(dayFrame)
        dayFrameToWorkouts.pop(dayFrame)
    except KeyError:
        pass
    dayFrames.pop(dayNum)
    dayFrame.destroy()

    if len(dayFrames) == 0:
        frame = ttk.Frame(scrollFrame)
        frame.grid(row=0, sticky=(N, W, E, S))
        ttk.Button(frame, text="Add Day", command=lambda curr = -1: addDay(curr)).grid(column=0, row=1)
        dayFrames.append(frame)
    else:
        for currDay in range(dayNum, len(dayFrames)):
            dayFrames[currDay].grid(row=currDay, sticky=(N, W, E, S))
            dayLabels[currDay]['text'] = 'Day ' + str(currDay+1) + ' : '
            dayButtons[currDay]['command'] = lambda arg = currDay+1: addDay(arg)
            #dayButtons[currDay]['text'] = "Add Day " + str(currDay)
        #confirmButton.grid(row=len(dayFrames), sticky=E)

def addWorkout(dayFrame, workNum):
    workFrame = ttk.Frame(dayFrame)
    if workNum == -1:
        frame = dayFrameToWorkFrames[dayFrame].pop()
        frame.destroy()
        workNum += 1

        workFrame.grid(row=workNum+1, sticky=(N, W, E, S))
       
        ttk.Label(workFrame, text="Excercise").grid(column=1, row=0)
        ttk.Label(workFrame, text="Sets").grid(column=2, row=0)
        ttk.Label(workFrame, text="Reps").grid(column=3, row=0)
        ttk.Label(workFrame, text="Weight").grid(column=4, row=0)
        ttk.Label(workFrame, text="Link").grid(column=5, row=0)
    else:
        workFrame.grid(row=workNum+1, sticky=(N, W, E, S))

    workFrames = dayFrameToWorkFrames[dayFrame]
    workFrames.insert(workNum, workFrame)

    if dayFrame not in dayFrameToWorkLabels:
        dayFrameToWorkLabels[dayFrame] = []
    workLabels = dayFrameToWorkLabels[dayFrame]
    workLabel = ttk.Label(workFrame, width=3, text=str(workNum+1)+". ")
    workLabel.grid(column=0, row=1)
    workLabels.insert(workNum, workLabel)

    currExcercise = StringVar()
    currSets = StringVar()
    currReps = StringVar()
    currWeight = StringVar()
    currLink = StringVar()
    if dayFrame not in dayFrameToWorkouts:
        dayFrameToWorkouts[dayFrame] = []
    workouts = dayFrameToWorkouts[dayFrame]
    workouts.insert(workNum, (currExcercise, currSets, currReps, currWeight, currLink))

    ttk.Entry(workFrame, width=40, textvariable=currExcercise).grid(column=1, row=1)
    ttk.Entry(workFrame, width=4, textvariable=currSets).grid(column=2, row=1)
    ttk.Entry(workFrame, width=12, textvariable=currReps).grid(column=3, row=1)
    ttk.Entry(workFrame, width=6, textvariable=currWeight).grid(column=4, row=1)
    ttk.Entry(workFrame, width=90, textvariable=currLink).grid(column=5, row=1)
    workButton = ttk.Button(workFrame, width=3, text="+", command=lambda arg1 = dayFrame, arg2 = workNum+1: addWorkout(arg1, arg2))
    workButton.grid(column=6, row=1)
    ttk.Button(workFrame, text="-", width=3, command=lambda arg1 = dayFrame, arg2 = workFrame: removeWorkout(arg1, arg2)).grid(column=7, row=1)

    if dayFrame not in dayFrameToWorkButtons:
        dayFrameToWorkButtons[dayFrame] = []
    workButtons = dayFrameToWorkButtons[dayFrame]
    workButtons.insert(workNum, workButton)
    for currWork in range(workNum+1, len(workFrames)):
        workFrames[currWork].grid(row=currWork+1, sticky=(N, W, E, S))
        workLabels[currWork]['text'] = str(currWork+1) + '. '
        workButtons[currWork]['command'] = lambda arg1 = dayFrame, arg2 = workNum: addWorkout(arg1, arg2)
    dayNum = dayFrames.index(dayFrame)
    dayButton = dayButtons[dayNum]
    try:
        dayButton.grid(row=dayButton.grid_info()['row']+1)
    except KeyError:
        pass
    

def removeWorkout(dayFrame, workFrame):
    workFrames = dayFrameToWorkFrames[dayFrame]
    workLabels = dayFrameToWorkLabels[dayFrame]
    workButtons = dayFrameToWorkButtons[dayFrame]
    workouts = dayFrameToWorkouts[dayFrame]
    try:
        workNum = workFrames.index(workFrame)
    except ValueError:
        return

    workFrames.pop(workNum)
    workFrame.destroy()
    workLabels.pop(workNum)
    workButtons.pop(workNum)
    workouts.pop(workNum)

    if len(workFrames) == 0:
        frame = ttk.Frame(dayFrame)
        frame.grid(row=1, sticky=(N, W, E, S))
        ttk.Label(frame, text="Add workout...").grid(column=0, row=0)
        ttk.Button(frame, width=3, text="+", command=lambda curr1 = dayFrame, curr2 = -1: addWorkout(curr1, curr2)).grid(column=1, row=0)
        workFrames.append(frame)
    else:
        for currWork in range(workNum, len(workFrames)):
            if currWork == 0:
                workFrame = workFrames[currWork]
                ttk.Label(workFrame, text="Excercise").grid(column=1, row=0)
                ttk.Label(workFrame, text="Sets").grid(column=2, row=0)
                ttk.Label(workFrame, text="Reps").grid(column=3, row=0)
                ttk.Label(workFrame, text="Weight").grid(column=4, row=0)
                ttk.Label(workFrame, text="Link").grid(column=5, row=0)
            workFrames[currWork].grid(row=currWork+1, sticky=(N, W, E, S))
            workLabels[currWork]['text'] = str(currWork+1) + '. '
            workButtons[currWork]['command'] = lambda arg1 = dayFrame, arg2 = workNum+1: addWorkout(arg1, arg2)
        dayNum = dayFrames.index(dayFrame)
        dayButton = dayButtons[dayNum]
        try:
            dayButton.grid(row=dayButton.grid_info()['row']-1)
        except KeyError:
            pass

def writeToFile():
    output=""
    for i in range(len(dayOfWeekList)):
        if dayFrames[i] not in dayFrameToWorkouts:
            continue
        output += dayOfWeekList[i].get() + "<|>" + workoutTypes[i].get() + "\n"
        workouts = dayFrameToWorkouts[dayFrames[i]]
        for j in range(len(workouts)):
            for elem in workouts[j]:
                output += elem.get() + "<|>"
            output = output[:-3]
            output += "\n"
        output+="\n"
    f = open("workoutdata.txt", "w")
    f.write(output)
    f.close()
    scrollFrame.destroy()

    for child in root.winfo_children():
        if child is not countTimeFrame:
            child.destroy()
    main()

    if displayFrame is not None:
        displayFrame.destroy()
        


def parseFile(file):
    # All three data structures below are just string, need to set them to a StringVar first
    dayToWorkouts = {}  # Pretty much dayFrameToWorkouts, but maps dayNum to workouts instead
    daysOfWeek = []  # Similar/same as dayOfWeekList
    workoutDescript = []  # Similar/same as workoutTypes

    input = ""
    dayNum = 0
    while True:
        currLine = file.readline()
        if currLine == "":
            break
        currLine = currLine[:-1]
        headerLine = currLine.split("<|>")
        daysOfWeek.append(headerLine[0])
        workoutDescript.append(headerLine[1])

        dayToWorkouts[dayNum] = []

        while True:
            currLine = file.readline()
            if currLine == "\n":
                break
            currLine = currLine[:-1]
            workoutLine = currLine.split("<|>")
            workout = (workoutLine[0], workoutLine[1], workoutLine[2], workoutLine[3], workoutLine[4])
            dayToWorkouts[dayNum].append(workout)

        dayNum += 1
    display(daysOfWeek, workoutDescript, dayToWorkouts)

def display(daysOfWeek, workoutDescript, dayToWorkouts):
    dayNum = date.today().weekday()

    # Debugging
    #dayNum = 3

    day = daysSuggestion[dayNum]
    
    if day not in daysOfWeek:
        header = ttk.Frame(root)
        header.grid(padx=10, pady=10, sticky=(N, W, E, S))
        ttk.Label(header, width=18, anchor=CENTER, text="Rest Day!!!!", font=dayFont).grid(row=0)
        frame = ttk.Frame(root)
        frame.grid(padx=10, pady=10, sticky=(N, W, E, S))
        ttk.Button(frame, text="Show All Workouts", command=lambda arg1 = daysOfWeek, arg2 = workoutDescript, arg3=dayToWorkouts: displayAll(arg1, arg2, arg3)).grid(row=1, column=0, padx=2)
        ttk.Button(frame, text="Edit All Workouts", command=lambda arg1 = -1, arg2 = daysOfWeek, arg3 = workoutDescript, arg4=dayToWorkouts: edit(arg1, arg2, arg3, arg4)).grid(row=1, column=1, padx=2)
    else:
        index = daysOfWeek.index(day)
        displayFrame = ttk.Frame(root)
        displayFrame.grid(row=0, padx=10)
        displayDay(displayFrame, index, daysOfWeek, workoutDescript, dayToWorkouts)

        frame = ttk.Frame(displayFrame)
        frame.grid(pady=5)
        ttk.Button(frame, text="Show All Workouts", command=lambda arg1 = daysOfWeek, arg2 = workoutDescript, arg3=dayToWorkouts: displayAll(arg1, arg2, arg3)).grid(row=2, column=0, padx=2)
        ttk.Button(frame, text="Edit", command=lambda arg1 = index, arg2 = daysOfWeek, arg3 = workoutDescript, arg4=dayToWorkouts: edit(arg1, arg2, arg3, arg4)).grid(row=2, column=1, padx=2)
        ttk.Button(frame, text="Edit All Workouts", command=lambda arg1 = -1, arg2 = daysOfWeek, arg3 = workoutDescript, arg4=dayToWorkouts: edit(arg1, arg2, arg3, arg4)).grid(row=2, column=2, padx=2)
    
        if countTimeFrame is None:
            setCounterAndTimer()

def displayAll(daysOfWeek, workoutDescript, dayToWorkouts):
    global displayFrame
    displayTop = Toplevel()
    displayTop.title('All Workouts')
    displayTop.columnconfigure(0, weight=1)
    displayTop.rowconfigure(0, weight=1)
    displayTop.minsize(883, 500)
    scrollFrame = ttk.Frame(displayTop, borderwidth=5, relief='solid')
    scrollFrame.grid(row=0, padx=5, pady=5, sticky=(N, E, S, W))
    innerFrame = ScrollFrame(scrollFrame).scrollFrame
    for i in range(len(daysOfWeek)):
        displayDay(innerFrame, i, daysOfWeek, workoutDescript, dayToWorkouts)

    ttk.Button(displayTop, text="Edit", command=lambda arg1 = -1, arg2 = daysOfWeek, arg3 = workoutDescript, arg4=dayToWorkouts: edit(arg1, arg2, arg3, arg4)).grid(pady=5)

def displayDay(container, dayNum, daysOfWeek, workoutDescript, dayToWorkouts):
    header = ttk.Frame(container)
    header.grid(sticky=(N, W, E, S))
    headerText = "Day " + str(dayNum+1) + " (" + daysOfWeek[dayNum] + "): " + workoutDescript[dayNum]
    ttk.Label(header, text=headerText, font=dayFont).grid()
    workoutFrame = ttk.Frame(container)
    workoutFrame.grid(sticky=(N, W, E, S))
    ttk.Label(workoutFrame, text="Exercise", foreground=HEAD_LETTER, background=HEAD_COLOR, width=EXCER_WIDTH, font=headFont).grid(row=0, column=0, sticky=(W, E))
    ttk.Label(workoutFrame, text="Sets", foreground=HEAD_LETTER, background=HEAD_COLOR, width=SR_WIDTH, font=headFont).grid(row=0, column=1, sticky=(W, E))
    ttk.Label(workoutFrame, text="Reps", foreground=HEAD_LETTER, background=HEAD_COLOR, width=SR_WIDTH, font=headFont).grid(row=0, column=2, sticky=(W, E))
    ttk.Label(workoutFrame, text="Weight", foreground=HEAD_LETTER, background=HEAD_COLOR, width=SR_WIDTH, font=headFont).grid(row=0, column=3, sticky=(W, E))
    #ttk.Label(workoutFrame, text="Link", foreground=HEAD_LETTER, background=HEAD_COLOR, font=headFont).grid(row=0, column=3, sticky=(W, E))
        
    workouts = dayToWorkouts[dayNum]
    for j in range(len(workouts)):
        ttk.Label(workoutFrame, text=str(j+1) + ". " + workouts[j][0], width=EXCER_WIDTH, relief='solid', font=excerFont).grid(row=j+1, column=0)
        ttk.Label(workoutFrame, text=workouts[j][1], width=SR_WIDTH, relief='solid', font=excerFont).grid(row=j+1, column=1)
        ttk.Label(workoutFrame, text=workouts[j][2], width=SR_WIDTH, relief='solid', font=excerFont).grid(row=j+1, column=2)
        ttk.Label(workoutFrame, text=workouts[j][3], width=SR_WIDTH, relief='solid', font=excerFont).grid(row=j+1, column=3)
        ttk.Button(workoutFrame, text="Guide", command=lambda l = workouts[j][4]: goToLink(l)).grid(row=j+1, column=4)

def edit(dayToEdit, daysOfWeek, workoutDescript, dayToWorkouts):
    global scrollFrame, confirmButton

    if len(daysOfWeek) == 0:
        new()
        return

    init()
    top = Toplevel()
    top.title('Edit')
    top.columnconfigure(0, weight=1)
    top.rowconfigure(0, weight=1)
    top.grab_set()
    if dayToEdit == -1:
        top.minsize(1060, 500)
    else:
        top.minsize(1060, 250)

    container = ttk.Frame(top, borderwidth=5, relief='solid')
    container.grid(row=0, padx=5, pady=5, sticky=(N, E, S, W))

    scrollFrame = ScrollFrame(container).scrollFrame

    for i in range(len(daysOfWeek)):
        dayFrame = ttk.Frame(scrollFrame)
        dayFrame.grid(row=i, sticky=(N, W, E, S))    
        dayFrames.append(dayFrame) # Update dayFrames

        if dayToEdit != -1 and i != dayToEdit:
            dayFrame.grid_remove()

        dayHeaderFrame = ttk.Frame(dayFrame)
        dayHeaderFrame.grid(column=0, row=0, sticky=(N, W, E, S))

        day = StringVar()
        day.set(daysOfWeek[i])
        dayOfWeekList.append(day) # Update dayOfWeekList

        dayLabel = ttk.Label(dayHeaderFrame, text='Day ' + str(i+1) + ' : ')
        dayLabel.grid(column=0, row=0)
        dayLabels.append(dayLabel)  # Update dayLabels
        dayCombo = ttk.Combobox(dayHeaderFrame, width=11, textvariable=day)
        dayCombo['values'] = daysSuggestion
        dayCombo.grid(column=1, row=0)

        type = StringVar()
        type.set(workoutDescript[i])
        workoutTypes.append(type)  # Update workoutTypes
        ttk.Entry(dayHeaderFrame, width=45, textvariable=type).grid(column=2, row=0)

        dayFrameToWorkFrames[dayFrame] = [] # Update dayFrameToWorkFrames
        dayFrameToWorkLabels[dayFrame] = [] # Update dayFrameToWorkLabels
        dayFrameToWorkouts[dayFrame] = [] # Update dayFrameToWorkouts
        dayFrameToWorkButtons[dayFrame] = [] # Update dayFrameToWorkButtons
        workouts = dayToWorkouts[i]

        for j in range(len(workouts)):
            workFrame = ttk.Frame(dayFrame)
            workFrame.grid(row=j+1, sticky=(N, W, E, S))

            if j == 0:
                ttk.Label(workFrame, text="Excercise").grid(column=1, row=0)
                ttk.Label(workFrame, text="Sets").grid(column=2, row=0)
                ttk.Label(workFrame, text="Reps").grid(column=3, row=0)
                ttk.Label(workFrame, text="Weight").grid(column=4, row=0)
                ttk.Label(workFrame, text="Link").grid(column=5, row=0)

            dayFrameToWorkFrames[dayFrame].append(workFrame)

            workLabel = ttk.Label(workFrame, width=3, text=str(j+1)+". ")
            workLabel.grid(column=0, row=1)
            dayFrameToWorkLabels[dayFrame].append(workLabel)

            currExcercise = StringVar()
            currExcercise.set(workouts[j][0])
            currSets = StringVar()
            currSets.set(workouts[j][1])
            currReps = StringVar()
            currReps.set(workouts[j][2])
            currWeight = StringVar()
            currWeight.set(workouts[j][3])
            currLink = StringVar()
            currLink.set(workouts[j][4])
            dayFrameToWorkouts[dayFrame].append((currExcercise, currSets, currReps, currWeight, currLink))

            ttk.Entry(workFrame, width=40, textvariable=currExcercise).grid(column=1, row=1)
            ttk.Entry(workFrame, width=4, textvariable=currSets).grid(column=2, row=1)
            ttk.Entry(workFrame, width=12, textvariable=currReps).grid(column=3, row=1)
            ttk.Entry(workFrame, width=6, textvariable=currWeight).grid(column=4, row=1)
            ttk.Entry(workFrame, width=90, textvariable=currLink).grid(column=5, row=1)

            workButton = ttk.Button(workFrame, width=3, text="+", command=lambda arg1 = dayFrame, arg2 = j+1: addWorkout(arg1, arg2))
            workButton.grid(column=6, row=1)
            ttk.Button(workFrame, text="-", width=3, command=lambda arg1 = dayFrame, arg2 = workFrame: removeWorkout(arg1, arg2)).grid(column=7, row=1)
            dayFrameToWorkButtons[dayFrame].append(workButton)

        addButton = ttk.Button(dayFrame, text="Add Day", command=lambda arg = i+1: addDay(arg))
        addButton.grid(column=0)
        removeButton = ttk.Button(dayHeaderFrame, text="Remove Day", command=lambda curr = dayFrame: removeDay(curr))
        removeButton.grid(column=3, row=0)
        dayButtons.append(addButton)  # Update dayButtons

        if dayToEdit != -1:
            addButton.grid_remove()
            removeButton.grid_remove()

    confirmButton = ttk.Button(top, text="Confrim", command=writeToFile)
    confirmButton.grid(pady=5)

def goToLink(link):
    webbrowser.get('windows-default').open(link)

def setCounterAndTimer():
    global count, countTimeFrame
    countTimeFrame = ttk.Frame(root)
    countTimeFrame.grid(row=1, pady=10)

    counterFrame = ttk.Frame(countTimeFrame)
    counterFrame.grid(row=0, column=0, padx=10)
    count = StringVar()
    count.set("00")
    ttk.Label(counterFrame, textvariable=count, relief='groove', font=countFont, background='#ffffff').grid(row=0, column=0, rowspan=3)

    s = ttk.Style()
    s.configure('big.TButton', font=('Helvetica', 19))

    ttk.Button(counterFrame, text="+", width=2, command=inc, style='big.TButton').grid(row=0, column=1)
    ttk.Button(counterFrame, text="-", width=2, command=dec, style='big.TButton').grid(row=1, column=1)
    ttk.Button(counterFrame, text='C', width=2, command=clear, style='big.TButton').grid(row=2, column=1)

    timerFrame = ttk.Frame(countTimeFrame)
    timerFrame.grid(row=0, column=1, padx=10)
    timer = Timer(timerFrame)
    timer.timer.grid()
    innerFrame = ttk.Frame(timerFrame)
    innerFrame.grid()
    ttk.Button(innerFrame, width=11, text="Start", command=timer.start).grid(row=0, column=0)
    ttk.Button(innerFrame, width=11, text="Reset", command=timer.reset).grid(row=0, column=1)

def inc(*arg):
    res = int(count.get()) + 1
    if res < 10:
        count.set('0' + str(res))
    else:
        count.set(res)

def dec():
    res = int(count.get()) - 1
    if res < 0:
        return
    if res < 10:
        count.set('0' + str(res))
    else:
        count.set(res)

def clear():
    count.set('00')

def main():
    try:
        file = open("workoutdata.txt", "r")
        if os.path.getsize('workoutdata.txt') == 0:
            editButton = ttk.Button(root, text="Add New Workout", command=new).grid()
        else:
            parseFile(file)
    except FileNotFoundError:
        editButton = ttk.Button(root, text="Add New Workout", command=new).grid()

if __name__ == "__main__":
    main()

root.mainloop()



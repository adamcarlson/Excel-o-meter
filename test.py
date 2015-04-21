__author__ = 'Adam Carlson'




from tkinter import ttk
from tkinter import *
from functools import partial
from tkinter import Image, PhotoImage


import fixedCanvasToolbar

def bla():
    print("yo")

colors = {
    'fg1' : '#23D400',
    'fg2' : '#7FD66D',
    'fg3' : '#D9D9D9',
    'bg': '#3B3B3B',
    'selected fg' : '#7FD66D',
    'selected bg' : '#2B2B2B'
}


class TabFrame(Frame):
    def __init__(self, parent, colorScheme, tabs):
        self.parent = parent
        self.colorScheme = colorScheme # dictionary {fg1, fg2, bg, selected fg, selected bg}
        self.tabs = tabs    # list of tuples [(tabName, tabFrame), ...]
        Frame.__init__(self.parent)
        self.initUIOutline()
        self.initUI()

    def initUIOutline(self):
        self.buttonFrame = Frame(self, bg=self.colorScheme['bg'], width=200)
        self.buttonFrame.grid(row=1, column=0, sticky='nw')

        self.contentFrame = Frame(self, bg=self.colorScheme['selected bg'])
        self.contentFrame.grid(row=1, column=1, sticky='nw', ipadx=5, ipady=5)

        self.currentFrame = Frame(self.contentFrame)
        self.currentFrame.grid(row=0, column=0)

    def initUI(self):
        self.tabButtons = [TabButton(self.buttonFrame, text, self.colorScheme, self.changeTabs, frame) for i, text, frame in enumerate(self.tabs)]
        for i, item in enumerate(self.tabButtons):
            item.grid(row=i, column=0, sticky='nw')

        self.changeTabs(self.tabButtons[0])

    def changeTabs(self, tabButton):
        for item in self.tabButtons:
            item.drawButton()

        tabButton.configure(fg=self.colorScheme['selected fg'], bg=self.colorScheme['selected bg'])
        tabButton.unbind_all()
        self.changeContentFrame(tabButton.frame)

    def changeContentFrame(self, frame):
        self.currentFrame.grid_remove()
        self.currentFrame = frame(self.contentFrame)
        self.grid(row=0, column=0, sticky='nw')


class TabButton(Label):
    def __init__(self, master, text, colorScheme, command, frame):
        Label.__init__(self, master, text=text, width=200, height=50)
        self.colorScheme = colorScheme
        self.command = command
        self.contentFrame = frame
        self.drawButton()

    def drawButton(self):
        self.config(fg=self.colorScheme['fg1'], bg=self.colorScheme['bg'], font=("Calibri", 16))
        self.bind("<Enter>", partial(self.color_config, self, self.colorScheme['fg2']))
        self.bind("<Leave>", partial(self.color_config, self, self.colorScheme['fg1']))
        self.bind("<Button-1>", partial(self.runCommand))

    def runCommand(self, widget):
        self.command(self)

    def color_config(self, widget, color, event):
        widget.configure(foreground=color)


class Simple(object):
    def __init__(self, x):
        self.x = x

    def changeX(self):
        self.x = self.x * 2

def changer(simpleObject):
    simpleObject.changeX()

class Complex(object):
    def __init__(self, simpleObject):
        self.simple = simpleObject

    def changeMyObject(self):
        self.simple.changeX()

class SuperComplex(object):
    def __init__(self, obTuple):
        self.obTuple = obTuple

class TheBreaker(object):
    def __init__(self, x):
        self.x = 10

    def funny(self, breaker):
        self.me = breaker


class SensorView(Frame):
    def __init__(self, parent, sensor):
        self.parent = parent
        self.sensorNum = sensor - 1
        Frame.__init__(self, self.parent, bg=colors['bgSecondary'])
        self.initUI()
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        self.rowconfigure(3, weight=1)
        self.columnconfigure(0, weight=1)

    def initUI(self):
        temp = [ActuallyWorkingFigureCanvas(sensorData.plotList[self.sensorNum][i], self) for i in range(3)]
        self.graphList = [GraphContainer(i+1, item, ActuallyWorkingToolbar(item, self)) for i, item in enumerate(temp)]

        for item in self.graphList:
            self.drawGraph(item)

    def drawGraph(self, item):
        item.canvas.show()
        item.canvas.get_tk_widget().grid(row=item.graphNumber, column=0, sticky='nsew', pady=0, padx=0)
        item.canvas.get_tk_widget().configure(bg=colors['bgSecondary'])
        item.canvas.get_tk_widget().bind("<Button-1>", functools.partial(self.expand, item=item))

    def packer(self, alreadyPacked):
        for item in self.graphList:
            if item.graphNumber != alreadyPacked.graphNumber:
                item.canvas.get_tk_widget().grid(row=item.graphNumber, column=0, sticky='nsew')

    def unpacker(self, leaveOut):
        for item in self.graphList:
            if item.graphNumber != leaveOut.graphNumber:
                item.canvas._tkcanvas.grid_remove()

    def expand(self, event, item):
        self.unpacker(item)
        item.canvas.rebinder()

        self.buttonFrame = Frame(self, height=25)
        self.buttonFrame.grid(row=0, column=0, sticky='nsew')

        if item.graphNumber != 1:
            LinkButton(self.buttonFrame, "Previous Graph", self.changeGraph, colors, commandParameters=(item, self.graphList[item.graphNumber-2])).grid(row=0, column=0, sticky='nsew')
        if item.graphNumber != 3:
            LinkButton(self.buttonFrame, "Next Graph", self.changeGraph, colors, commandParameters=(item, self.graphList[item.graphNumber])).grid(row=0, column=2, sticky='nsew')

        LinkButton(self.buttonFrame, "Full View", self.fullView, colors, commandParameters=item).grid(row=0, column=1, sticky='nsew')
        #filterButton = LinkButton(self.buttonFrame, "Apply Filter", self.changeGraph, colors, item)

        item.toolbar.update()
        item.toolbar.show(item.graphNumber)

    def changeGraph(self, vars):
        currentItem, nextItem = vars
        self.fullView(currentItem)
        self.expand(None, nextItem)

    def fullView(self, item):
        self.buttonFrame.grid_remove()
        item.toolbar.hide()
        item.canvas.get_tk_widget().bind("<Button-1>", functools.partial(self.expand, item=item))
        self.packer(item)

    def filterGraph(self, itemNum):
        pass

    def kill(self):
        # if something changed saved[1] = False
        pass


def click(event):
    print("B-1")

def dClick(event):
    print("DB-2")


widget = Button(None, text='Hello event world')
widget.pack()
widget.bind('<Button-1>', click)             # bind left mouse clicks
widget.bind('<Double-1>', dClick)              # bind double left clicks
widget.mainloop()






"""
A simple example of an animated plot... In 3D!

import numpy as np
import matplotlib.pyplot as plt
import mpl_toolkits.mplot3d.axes3d as plt3
import matplotlib.animation as animation

record_dtype = np.dtype([('x_data', np.float32), ('y_data', np.float32), ('z_data', np.float32)])
x = np.fromfile('s1.dat', dtype=record_dtype)
x_data = x['x_data']
y_data = x['y_data']
z_data = x['z_data']


myLine = [[x_data[i], y_data[i], z_data[i]] for i in range(np.size(x_data))]


def update_lines(num, data, line):
    if num > 20:
        x = num - 20
    else:
        x = 0
    line.set_data([data[i][0] for i in range(x, num)], [ data[i][1] for i in range(x, num)])
    line.set_3d_properties([data[i][2] for i in range(x, num)])
    return line

# Attaching 3D axis to the figure
fig = plt.figure()
ax = plt3.Axes3D(fig)

# Fifty lines of random 3-D lines
#data = [Gen_RandLine(10000, 3) for index in range(1)]


# Creating fifty line objects.
# NOTE: Can't pass empty arrays into 3d version of plot()
#line = ax.plot(myLine[0, 0:1], myLine[1, 0:1], myLine[2, 0:1])[0]
line = ax.plot([myLine[0][0], myLine[1][0]],[myLine[0][1], myLine[1][1]],[myLine[0][2], myLine[1][2]])[0]

# Setting the axes properties
ax.set_xlim3d([0.0, 1.0])
ax.set_xlabel('X')

ax.set_ylim3d([0.0, 1.0])
ax.set_ylabel('Y')

ax.set_zlim3d([0.0, 1.0])
ax.set_zlabel('Z')

ax.set_title('3D Test')

print(np.size(x_data))
# Creating the Animation object
line_ani = animation.FuncAnimation(fig, update_lines, frames=np.size(x_data), fargs=(myLine, line),
                              interval=1, blit=False)

plt.show()
"""
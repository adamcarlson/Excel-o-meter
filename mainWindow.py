__author__ = 'Adam Carlson'

import sys
import matplotlib
matplotlib.use('TkAgg')

from tkinter import *

from tkinter.filedialog import askopenfilename

from numpy import arange, sin, pi, dtype, fromfile
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.backend_bases import key_press_handler
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import matplotlib.animation as ani
import functools
import math

import classes
import sensorData as sd

# Constants:
FRAME, CANVAS, TOOLBAR = 0, 1, 2
gX, gY, gZ = 0, 1, 2


class WelcomeWindow(Tk):
    def __init__(self):
        Tk.__init__(self)
        self.isSensorView = 0
        self.protocol("WM_DELETE_WINDOW", self.fOnExit)
        #self.makeMenuBar()
        self.initUI()
        #MainWindow(self)

    def initUI(self):
        self.title("Excel-o-meter")
        self.geometry("500x500")
        self.mainFrame = Frame(self)
        self.mainFrame.pack(side=TOP, fill=BOTH, expand=1)
        importButton = Button(self.mainFrame, text="IMPORT", command=self.fImportData)
        openButton = Button(self.mainFrame, text="OPEN", command=self.fOpen)
        importButton.pack(side=TOP, fill=BOTH, expand=1)
        openButton.pack(side=TOP, fill=BOTH, expand=1)


    def makeMenuBar(self):
        menuBar = Menu(self)
        menuBar.config(tearoff=0)
        self.config(menu=menuBar)

        fileMenu = Menu(menuBar)
        fileMenu.config(tearoff=0)
        fileMenu.add_command(label="Import...", command=self.fImportData)
        fileMenu.add_command(label="Open...", command=self.fOpen)
        fileMenu.add_command(label="Save As...", command=self.fSaveAs)
        fileMenu.add_command(label="Save", command=self.fSave)
        fileMenu.add_separator()
        fileMenu.add_command(label="Exit", command=self.fOnExit)
        menuBar.add_cascade(label="File", menu=fileMenu)

        editMenu = Menu(menuBar)
        editMenu.config(tearoff=0)
        editMenu.add_command(label='Filter...', command=self.eFilter)
        menuBar.add_cascade(label='Edit', menu=editMenu)

        viewMenu = Menu(menuBar)
        viewMenu.config(tearoff=0)
        viewMenu.add_command(label='Home', command=self.vHome)
        viewMenu.add_command(label='Sensor1', command=self.vSensor1)
        viewMenu.add_command(label='Sensor2', command=self.vSensor2)
        viewMenu.add_command(label='Sensor3', command=self.vSensor3)
        menuBar.add_cascade(label='View', menu=viewMenu)

        helpMenu = Menu(menuBar)
        helpMenu.config(tearoff=0)
        helpMenu.add_command(label='Help', command=self.hHelp)
        menuBar.add_cascade(label='Help', menu=helpMenu)


    #File Menu
    def fImportData(self):
        sensorData.importData()
        self.makeMenuBar()
        self.mainFrame.pack_forget()
        self.mainWindow = MainWindow(self)

    def sensorSelect(self, sensor):
        self.mainWindow.mainFrame.pack_forget()
        self.sensorViewFrame = Frame(self)
        self.sensorViewFrame.pack(side=TOP, fill=BOTH, expand=1)
        SensorView(self.sensorViewFrame, sensor)
        self.isSensorView = 1

    def homeView(self):
        if self.isSensorView == 1:
            self.sensorViewFrame.pack_forget()
            self.sensorViewFrame.destroy()
            self.isSensorView = 0
        self.mainWindow.mainFrame.pack(side=TOP, fill=BOTH, expand=1)

    def fOpen(self):
        sensorData.newData(classes.openSaveFile())
        self.makeMenuBar()
        self.mainFrame.pack_forget()
        self.mainWindow = MainWindow(self)

    def fSaveAs(self):
        classes.saveFile(sensorData)

    def fSave(self):
        classes.saveFile(sensorData)

    def fOnExit(self):
        sys.exit()

    #Edit Menu
    def eFilter(self):
        pass

    #ViewMenu
    def vHome(self):
        self.homeView()

    def vSensor1(self):
        self.homeView()
        self.sensorSelect(0)

    def vSensor2(self):
        self.homeView()
        self.sensorSelect(1)

    def vSensor3(self):
        self.homeView()
        self.sensorSelect(2)

    # Help Menu
    def hHelp(self):
        pass

class MainWindow(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.parent = parent
        self.initUI()


    def initUI(self):
        self.parent.title("Excel-o-meter")
        self.parent.geometry("1500x900")
        self.mainFrame = Frame(self.parent)
        self.mainFrame.pack(side=TOP, fill=BOTH, expand=1)

        sensorList = [Frame(self.mainFrame) for i in range(3)]
        for i, item in enumerate(sensorList):
            if i == 0:
                self.draw4DG(item)

            topLabel = Label(item, text="Sensor {}".format(i+1))
            topLabel.pack(side=TOP, fill=X, expand=1)

            item.pack(side=LEFT, fill=BOTH, expand=1)

    def draw4DG(self, graphFrame):
        sensorData.draw4DGraph(graphFrame, 1, sensorData.s1DList)

class SensorView(Frame):
    def __init__(self, parent, sensor):
        Frame.__init__(self, parent)
        self.parent = parent
        self.sensor = sensor
        self.init()

    def init(self):

        self.frameList = []
        for i in range(3):
            self.frameList.append(Frame(self.parent))
        secondaryFrameList = []
        for item in self.frameList:
            secondaryFrameList.append(Frame(item))
            secondaryFrameList.append(Frame(item))

        self.objectList = []
        for i, item in enumerate(secondaryFrameList):
            canvas = classes.ActuallyWorkingFigureCanvas(sensorData.SmallPlotList[self.sensor][i], item)
            self.objectList.append((item, canvas, classes.ActuallyWorkingToolbar(canvas, item)))
            self.objectList[i][TOOLBAR].update()

        axisList = ['X','Y','Z']
        for i, item in enumerate(self.frameList):
            self.drawLabel(item, "Sensor {} {}".format(self.sensor + 1, axisList[i]))

        for i, item in enumerate(self.objectList):
            self.drawGraph(item, i)
            self.packer(item, i)

        for item in self.frameList:
            item.pack(side=TOP, fill=BOTH, expand=1)

    def drawLabel(self, box, text):
        topLabel = Label(box, text=text)
        topLabel.pack(side=TOP, fill=BOTH, expand=0)

    def drawGraph(self, item, i):
        canvas = item[CANVAS]
        canvas.show()
        canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
        canvas.get_tk_widget().bind("<Button-1>", functools.partial(self.expand, itemNum=i))

    def packer(self, item, i):
        packList = [LEFT, RIGHT] * 6
        item[FRAME].pack(side=packList[i], fill=BOTH, expand=1)

    def unpacker(self, itemNum):
        frameListNum = math.floor(itemNum / 2)
        if frameListNum == math.floor((itemNum + 1) / 2):
            remove = itemNum + 1
        else:
            remove = itemNum - 1

        self.objectList[remove][FRAME].pack_forget()
        self.objectList[remove][FRAME].pack_forget()

        for i, item in enumerate(self.frameList):
            if i != frameListNum:
                item.pack_forget()

    def expand(self, event, itemNum):
        canvas = self.objectList[itemNum][CANVAS]
        graphFrame = self.objectList[itemNum][FRAME]
        toolbar = self.objectList[itemNum][TOOLBAR]

        self.unpacker(itemNum)
        canvas._tkcanvas.pack_forget()
        canvas.rebinder()

        self.buttonFrame = Frame(graphFrame)
        leftButtons = Frame(self.buttonFrame, width=300, height=50)
        rightButtons = Frame(self.buttonFrame, width=300, height=50)
        middleButtons = Frame(self.buttonFrame)

        leftButtons.pack_propagate(0)
        rightButtons.pack_propagate(0)

        leftButtons.pack(side=LEFT, fill=X)
        rightButtons.pack(side=RIGHT, fill=X)
        middleButtons.pack(side=TOP)
        self.buttonFrame.pack(side=TOP, fill=BOTH)

        if itemNum != 0:
            prevGButton = Button(leftButtons, text="Previous Graph", command=functools.partial(self.changeGraph, i=itemNum-1, itemNum=itemNum))
            if itemNum != 1:
                prevSButton = Button(leftButtons, text="Previous Sensor", command=functools.partial(self.changeGraph, i=itemNum-2, itemNum=itemNum))
                prevSButton.pack(side=LEFT)
            prevGButton.pack(side=LEFT)
        if itemNum != 5:
            nextGButton = Button(rightButtons, text="Next Graph", command=functools.partial(self.changeGraph, i=itemNum+1, itemNum=itemNum))
            if itemNum != 4:
                nextSButton = Button(rightButtons, text="Next Sensor", command=functools.partial(self.changeGraph, i=itemNum+2, itemNum=itemNum))
                nextSButton.pack(side=RIGHT)
            nextGButton.pack(side=RIGHT)

        backButton = Button(middleButtons, text="Full View", command=functools.partial(self.fullView, i=itemNum))
        backButton.pack(side=LEFT)
        filterButton = Button(middleButtons, text="Apply Filter", command=functools.partial(self.filterGraph, itemNum=itemNum))
        filterButton.pack(side=RIGHT)

        canvas._tkcanvas.pack(side=TOP, fill=BOTH, expand=1)
        toolbar.show()

    def changeGraph(self, i, itemNum):
        self.fullView(itemNum)
        self.expand(0, i)


    def fullView(self, i):

        self.buttonFrame.pack_forget()
        self.objectList[i][TOOLBAR].hide()
        self.objectList[i][TOOLBAR].releaseButton()

        self.objectList[i][FRAME].pack_forget()
        self.objectList[i][CANVAS].get_tk_widget().bind("<Button-1>", functools.partial(self.expand, itemNum=i))
        self.frameList[math.floor(i/2)].pack_forget()

        for i, item in enumerate(self.objectList):
            self.packer(item, i)

        for item in self.frameList:
            item.pack(side=TOP, fill=BOTH, expand=1)

    def filterGraph(self, itemNum):
        pass


if __name__ == '__main__':
    sensorData = sd.SensorData(100)
    app = WelcomeWindow()
    app.mainloop()
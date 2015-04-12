__author__ = 'Adam Carlson'

import sys
import matplotlib
matplotlib.use('TkAgg')

from tkinter import messagebox
from tkinter import *
from functools import partial

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


from fixedCanvasToolbar import ActuallyWorkingFigureCanvas, ActuallyWorkingToolbar
from extraUIElements import TabFrame, TitleLogo, LinkButton
import sensorData as sd

# Constants:
FRAME, CANVAS, TOOLBAR = 0, 1, 2
gX, gY, gZ = 0, 1, 2

colors = {
    'fg1' : '#23D400',
    'fg2' : '#7FD66D',
    'fg3' : '#D9D9D9',
    'bg': '#3B3B3B',
    'selected fg' : '#7FD66D',
    'selected bg' : '#2B2B2B'
}


class MainApp(Tk):
    def __init__(self):
        Tk.__init__(self)
        self.protocol("WM_DELETE_WINDOW", self.fOnExit)

        self.isSensorView = 0

        self.makeMenuBar()
        self.currentFrame = HomeWindow(self)
        self.currentFrame.pack(side=TOP, fill=BOTH, expand=1)

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

        helpMenu = Menu(menuBar)
        helpMenu.config(tearoff=0)
        helpMenu.add_command(label='Help', command=self.hHelp)
        menuBar.add_cascade(label='Help', menu=helpMenu)

    def changeFrame(self, newFrame):
        self.currentFrame.pack_forget()
        self.currentFrame.destroy()
        self.currentFrame = newFrame(self)
        self.currentFrame.pack(side=TOP, fill=BOTH, expand=1)

    def showSaveDialogue(self):
        return messagebox.askyesno("Excelometer", "Unsaved changes have been made.\nWould you like to save before exiting?")

    #File Menu
    def fImportData(self):
        sensorData.importData()
        self.changeFrame(RunView)

    def fOpen(self):
        sensorData.newData(sd.openSaveFile())
        self.changeFrame(RunView)

    def fSaveAs(self):
        runTitle = sd.saveFile(sensorData)
        sensorData.runData['runTitle'] = runTitle
        sensorData.saved = [True, True]

    def fSave(self):
        if sensorData.saved[0] == False:
            self.fSaveAs()
        elif sensorData.saved[1] == False:
            sd.saveFile(sensorData, sensorData.runData['runTitle'])
            sensorData.saved = [True, True]

    def fOnExit(self):
        if sensorData.saved[1] == False:
            if(self.showSaveDialogue()):
                self.fSave()
        sys.exit()

    #Edit Menu
    def eFilter(self):
        pass

    # Help Menu
    def hHelp(self):
        pass

class HomeWindow(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent, bg='#3B3B3B')
        self.parent = parent
        self.parent.resizable(0, 0)
        self.initUI()

    def initUI(self):
        self.parent.title("Excelometer - Start Page")

        TitleLogo(self, 'elogo.png').grid(row=0, column=0, columnspan=3)

        lineFrameH1 = Frame(self, bg="#2B2B2B", height=2, width=1000)
        lineFrameH1.grid(row=1, column=0, columnspan=3, sticky='nw')

        lineFrameV1 = Frame(self, bg="#2B2B2B", height=500, width=2)
        lineFrameV1.grid(row=2, column=1, rowspan=2, sticky='n')

        startFrame = Frame(self, bg='#3B3B3B', height=200)
        startFrame.grid(row=2, column=0, sticky='nw')

        quickSelectFrame = Frame(self, bg='#3B3B3B')
        quickSelectFrame.grid(row=2, column=2, rowspan=2, sticky='nw')

        recentsFrame = Frame(self, bg='#3B3B3B', width=100, height=100)
        recentsFrame.grid(row=3, column=0, padx=2, pady=2, sticky='nw')

        Label(startFrame, text="Start", font=("Calibri", 20), bg='#3B3B3B', fg='#D9D9D9').grid(row=0, sticky='nw', padx=40, pady=5)

        importButton = LinkButton(startFrame, "Import data...", self.parent.fImportData, colors)
        importButton.grid(row=1, sticky='w', padx=40)
        openButton = LinkButton(startFrame, "Open...", self.parent.fOpen, colors)
        openButton.grid(row=2, sticky='w', padx=40)

        Label(recentsFrame, text="Recent", font=("Calibri", 20), bg='#3B3B3B', fg='#D9D9D9').grid(row=0, sticky='nw', padx=40, pady=5)

        Label(quickSelectFrame, text="Quick Select", font=("Calibri", 20), bg='#3B3B3B', fg='#D9D9D9').grid(row=0, sticky='nw', padx=40, pady=5)

class RunView(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.parent = parent
        self.parent.resizable(0, 0)
        self.descriptionText = ''
        self.initUI()

    def initUI(self):
        self.parent.title("Excelometer - {}".format(sensorData.runData['runTitle']))

        runTitle = Label(self, text=sensorData.runData['runTitle'])
        runTitle.grid(row=0, column=0, sticky='n')

        lineFrameH1 = Frame(self, bg="#2B2B2B", height=2, width=1006)
        lineFrameH1.grid(row=1, column=0, columnspan=3, sticky='nw')

        middleFrame = Frame(self)
        middleFrame.grid(row=2, column=0)

        timeLabel = Label(middleFrame, text='Run Durration: {}'.format(sensorData.runData['runTime']))
        timeLabel.grid(row=0, column=0, sticky='nw')
        dateLabel = Label(middleFrame, text=sensorData.runData['runDate'])
        dateLabel.grid(row=0, column=1, sticky='ne')

        tabs = [
            ('Notes', NoteView),
        ]
        for i in range(sensorData.numberOfSensors):
            tabs.append(('Sensor {}'.format(i+1), SensorView))

        content = TabFrame(self, colors, tabs)
        content.grid(row=3, column=0, sticky='s')

class NoteView(Frame):
    def __int__(self, parent):
        self.parent = parent
        Frame.__init__(self.parent)
        self.initUI()

    def initUI(self):
        descriptionBox = Text(self, width=124, height=20)
        descriptionBox.grid(row=1, column=0, columnspan=2)

class SensorView(Frame):
    def __init__(self, parent, sensor):
        self.parent = parent
        self.sensorNum = sensor - 1
        Frame.__init__(self, self.parent)
        self.initUI()

    def initUI(self):
        temp = [ActuallyWorkingFigureCanvas(sensorData.plotList[self.sensorNum][i], self) for i in range(3)]
        self.graphList = [(item, ActuallyWorkingToolbar(item, self)) for item in temp]

        for i in range(3):
            self.drawGraph(self.graphList[i], i)

    def packer(self):
        for i in range(3):
            self.graphList[i][0].get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)

    def drawGraph(self, item, i):
        canvas = item[0]
        canvas.show()
        canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
        canvas.get_tk_widget().bind("<Button-1>", functools.partial(self.expand, itemNum=i))

    def unpacker(self):
        for graph, toolbar in self.graphList:
            graph._tkcanvas.pack_forget()

    def expand(self, event, itemNum):
        canvas = self.graphList[itemNum][0]
        toolbar = self.graphList[itemNum][1]

        self.unpacker()
        canvas.rebinder()

        self.buttonFrame = Frame(self)
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
            prevGButton.pack(side=LEFT)
        if itemNum != 3:
            nextGButton = Button(rightButtons, text="Next Graph", command=functools.partial(self.changeGraph, i=itemNum+1, itemNum=itemNum))
            nextGButton.pack(side=RIGHT)

        backButton = Button(middleButtons, text="Full View", command=functools.partial(self.fullView, i=itemNum))
        backButton.pack(side=LEFT)
        filterButton = Button(middleButtons, text="Apply Filter", command=functools.partial(self.filterGraph, itemNum=itemNum))
        filterButton.pack(side=RIGHT)

        canvas._tkcanvas.pack(side=TOP, fill=BOTH, expand=1)
        toolbar.update()
        toolbar.show()

    def changeGraph(self, i, itemNum):
        self.fullView(itemNum)
        self.expand(0, i)


    def fullView(self, i):
        self.buttonFrame.pack_forget()
        self.graphList[i][1].hide()
        self.graphList[i][1].releaseButton()
        self.graphList[i][0]._tkcanvas.pack_forget()
        self.graphList[i][0]._tkcanvas.bind("<Button-1>", functools.partial(self.expand, itemNum=i))

        self.packer()

    def filterGraph(self, itemNum):
        pass


if __name__ == '__main__':
    sensorData = sd.SensorData()
    app = MainApp()
    app.mainloop()
__author__ = 'Adam Carlson'

import matplotlib
matplotlib.use('TkAgg')

from tkinter import *
from numpy import arange, sin, pi
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
import functools

f = Figure(figsize=(5,1), dpi=100)
a = f.add_subplot(111)
t = arange(0.0,3.0,0.01)
s = sin(2*pi*t)

a.plot(t,s)


class MainWindow(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.parent = parent
        self.initUI()


    def initUI(self):
        self.parent.title("Excel-o-meter")
        self.parent.geometry("1500x900")

        menuBar = Menu(self.parent)
        menuBar.config(tearoff=0)
        self.parent.config(menu=menuBar)
        #self.singleGraph = Frame(self.parent)

        self.frameList = []
        for i in range(3):
            self.frameList.append(Frame(self.parent))
        secondaryFrameList = []
        for item in self.frameList:
            secondaryFrameList.append(Frame(item))
            secondaryFrameList.append(Frame(item))

        self.objectList = []
        labelList = ['Acceleration', 'Velocity'] * 6
        for i, item in enumerate(secondaryFrameList):
            self.objectList.append((item, FigureCanvasTkAgg(f, item), f, Label(item, text=labelList[i])))

        for i, item in enumerate(self.frameList):
            self.drawLabel(item, "Sensor {}".format(i+1))

        self.bindList=[]
        for i, item in enumerate(self.objectList):
            self.bindList.append(self.drawGraph(item, i))

        for i, item in enumerate(self.objectList):
            self.packer(item, i)

        for item in self.frameList:
            item.pack(side=TOP, fill=BOTH, expand=1)

        fileMenu = Menu(menuBar)
        fileMenu.config(tearoff=0)
        fileMenu.add_command(label="Import...", command=self.importData)
        fileMenu.add_command(label="Open...", command=self.open)
        fileMenu.add_command(label="Save As...", command=self.saveAs)
        fileMenu.add_command(label="Save", command=self.save)
        fileMenu.add_separator()
        fileMenu.add_command(label="Exit", command=self.onExit)
        menuBar.add_cascade(label="File", menu=fileMenu)

        editMenu = Menu(menuBar)
        editMenu.config(tearoff=0)
        editMenu.add_command(label='Filter...', command=self.filter)
        menuBar.add_cascade(label='Edit', menu=editMenu)

        helpMenu = Menu(menuBar)
        helpMenu.config(tearoff=0)
        helpMenu.add_command(label='Help', command=self.help)
        menuBar.add_cascade(label='Help', menu=helpMenu)

    def packer(self, item, i):
        packList = [LEFT, RIGHT] * 6

        item[3].pack(side=TOP, fill=BOTH, expand=0)
        item[0].pack(side=packList[i], fill=BOTH, expand=1)

    def unpacker(self, singleGraph):
        frameListNum = [0, 0, 1, 1, 2, 2]
        x = 0

        for i, item in enumerate(self.objectList):
            if item != singleGraph:
                item[0].pack_forget()
                item[3].pack_forget()
            else:
                x = frameListNum[i]

        return x

    def drawLabel(self, box, text):
        topLabel = Label(box, text=text)
        topLabel.pack(side=TOP, fill=BOTH, expand=0)

    def drawGraph(self, item, i):
        canvas = item[1]
        canvas.show()
        canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
        bindID = canvas.get_tk_widget().bind("<Button-1>", functools.partial(self.expand, item=item, itemNum=i))
        canvas._tkcanvas.pack(side=TOP, fill=BOTH, expand=1)
        return bindID

    def expand(self, event, item, itemNum):
        canvas = item[1]
        graphFrame = item[0]
        self.buttonFrame = Frame(graphFrame)
        middleButtons = Frame(self.buttonFrame)

        frameListNum = self.unpacker(item)
        for i, item in enumerate(self.frameList):
            if i != frameListNum:
                item.pack_forget()
        canvas._tkcanvas.pack_forget()
        canvas.get_tk_widget().unbind("<Button-1>", self.bindList[itemNum])

        if itemNum != 0:
            prevGButton = Button(self.buttonFrame, text="Previous Graph", command=functools.partial(self.changeGraph, i=itemNum-1, graphFrame=graphFrame, frameNum=frameListNum, itemNum=itemNum))
            if itemNum != 1:
                prevSButton = Button(self.buttonFrame, text="Previous Sensor", command=functools.partial(self.changeGraph, i=itemNum-2, graphFrame=graphFrame, frameNum=frameListNum, itemNum=itemNum))
                prevSButton.pack(side=LEFT)
            prevGButton.pack(side=LEFT)
        if itemNum != 5:
            nextGButton = Button(self.buttonFrame, text="Next Graph", command=functools.partial(self.changeGraph, i=itemNum+1, graphFrame=graphFrame, frameNum=frameListNum, itemNum=itemNum))
            if itemNum != 4:
                nextSButton = Button(self.buttonFrame, text="Next Sensor", command=functools.partial(self.changeGraph, i=itemNum+2, graphFrame=graphFrame, frameNum=frameListNum, itemNum=itemNum))
                nextSButton.pack(side=RIGHT)
            nextGButton.pack(side=RIGHT)

        backButton = Button(middleButtons, text="Full View", command=functools.partial(self.fullView, i=itemNum, graphFrame=graphFrame, frameNum=frameListNum))
        backButton.pack(side=LEFT)
        filterButton = Button(middleButtons, text="Apply Filter", command=functools.partial(self.filterGraph, item=item))
        filterButton.pack(side=RIGHT)

        middleButtons.pack(side=TOP)
        self.buttonFrame.pack(side=TOP, fill=BOTH)

        self.toolbar = NavigationToolbar2TkAgg(canvas, graphFrame)
        self.toolbar.update()
        canvas._tkcanvas.pack(side=TOP, fill=BOTH, expand=1)

    def changeGraph(self, i, graphFrame, frameNum, itemNum):
        self.fullView(itemNum, graphFrame, frameNum)
        self.expand(0,self.objectList[i], i)


    def fullView(self, i, graphFrame, frameNum):

        self.buttonFrame.pack_forget()
        self.toolbar.destroy()
        graphFrame.pack_forget()
        self.bindList[i] = self.objectList[i][1].get_tk_widget().bind("<Button-1>", functools.partial(self.expand, item=self.objectList[i], itemNum=i))
        self.frameList[frameNum].pack_forget()
        for item in self.objectList:
            item[3].pack_forget()

        for i, item in enumerate(self.objectList):
            self.packer(item, i)

        for item in self.frameList:
            item.pack(side=TOP, fill=BOTH, expand=1)



    def filterGraph(self, item):
        pass

    #File Menu
    def importData(self):
        pass

    def open(self):
        pass

    def saveAs(self):
        pass

    def save(self):
        pass

    def onExit(self):
        self.quit()

    #Edit Menu
    def filter(self):
        pass

    # Help Menu
    def help(self):
        pass



if __name__ == '__main__':
    root = Tk()
    #root.geometry('250x150+300+300')
    app = MainWindow(root)
    root.mainloop()
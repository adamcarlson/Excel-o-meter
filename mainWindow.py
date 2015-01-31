__author__ = 'Adam Carlson'

import matplotlib
matplotlib.use('TkAgg')

from tkinter import *
from numpy import arange, sin, pi
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure

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

        menuBar = Menu(self.parent)
        menuBar.config(tearoff=0)
        self.parent.config(menu=menuBar)
        #mainFrame = Frame(self.parent, width=1500, height=800, bg="#555")
        #mainFrame.pack()

        self.frameList = []
        for i in range(3):
            self.frameList.append(Frame(self.parent))
        secondaryFrameList = []
        for item in self.frameList:
            secondaryFrameList.append(Frame(item))
            secondaryFrameList.append(Frame(item))
        self.objectList = []
        for item in secondaryFrameList:
            self.objectList.append((item, FigureCanvasTkAgg(f, item)))

        for i, item in enumerate(self.frameList):
            self.drawLabel(item, "Sensor {}".format(i+1))

        for item in self.objectList:
            self.drawGraph(item[1], item[0])

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
        labelList = ['Acceleration', 'Velocity'] * 6
        packList = [LEFT, RIGHT] * 6

        label = Label(item[0], text=labelList[i])
        label.pack(side=TOP, fill=BOTH, expand=0)
        item[0].pack(side=packList[i], fill=BOTH, expand=1)

    def drawLabel(self, box, text):
        topLabel = Label(box, text=text)
        topLabel.pack(side=TOP, fill=BOTH, expand=0)

    def drawGraph(self, canvas, box):
        canvas.show()
        canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
        canvas.get_tk_widget().bind("<Button-1>", self.expand)
        #toolbar = NavigationToolbar2TkAgg(canvas, box)
        #toolbar.update()
        canvas._tkcanvas.pack(side=TOP, fill=BOTH, expand=1)

    def expand(self):
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
__author__ = 'Adam Carlson'

import matplotlib
matplotlib.use('TkAgg')

from tkinter import *
from numpy import arange, sin, pi
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure

f = Figure(figsize=(5,4), dpi=100)
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
        topFrame = Frame(self.parent)
        tfl = Frame(topFrame)
        tfr = Frame(topFrame)
        bottomFrame = Frame(self.parent)
        bfl = Frame(bottomFrame)
        bfr = Frame(bottomFrame)

        canvas = FigureCanvasTkAgg(f, tfl)
        canvas.show()
        canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
        toolbar = NavigationToolbar2TkAgg(canvas, tfl)
        toolbar.update()
        canvas._tkcanvas.pack(side=TOP, fill=BOTH, expand=1)

        canvas1 = FigureCanvasTkAgg(f, tfr)
        canvas1.show()
        canvas1.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
        toolbar1 = NavigationToolbar2TkAgg(canvas1, tfr)
        toolbar1.update()
        canvas1._tkcanvas.pack(side=TOP, fill=BOTH, expand=1)

        canvas2 = FigureCanvasTkAgg(f, bfl)
        canvas2.show()
        canvas2.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
        toolbar2 = NavigationToolbar2TkAgg(canvas2, bfl)
        toolbar2.update()
        canvas2._tkcanvas.pack(side=TOP, fill=BOTH, expand=1)

        canvas3 = FigureCanvasTkAgg(f, bfr)
        canvas3.show()
        canvas3.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
        toolbar3 = NavigationToolbar2TkAgg(canvas3, bfr)
        toolbar3.update()
        canvas3._tkcanvas.pack(side=TOP, fill=BOTH, expand=1)

        tfl.pack(side=LEFT, fill=BOTH, expand=1)
        tfr.pack(side=RIGHT, fill=BOTH, expand=1)
        topFrame.pack(side=TOP, fill=BOTH, expand=1)
        bfl.pack(side=LEFT, fill=BOTH, expand=1)
        bfr.pack(side=RIGHT, fill=BOTH, expand=1)
        bottomFrame.pack(side=TOP, fill=BOTH, expand=1)


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
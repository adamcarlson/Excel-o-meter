
__author__ = 'Adam Carlson'

from tkinter import Frame, Label, PhotoImage
from tkinter import TOP, BOTH
from functools import partial


class LinkButton(Label):
    def __init__(self, master, text, command, colorScheme, **kwargs):
        width = kwargs.get('width', 0)
        height = kwargs.get('height', 0)
        if width == 0 and height == 0:
            Label.__init__(self, master, text=text)
        else:
            Label.__init__(self, master, text=text, width=width, height=height)
        self.colorScheme = colorScheme
        self.command = command
        self.commandParameters = kwargs.get('commandParameters', None)
        self.text = text
        self.drawButton()

    def drawButton(self):
        self.selected = False
        self.config(fg=self.colorScheme['textClickable'], bg=self.colorScheme['bgNormal'], font=("Calibri", 16))
        self.bind("<Enter>", partial(self.color_config, self, self.colorScheme['textHover']))
        self.bind("<Leave>", partial(self.color_config, self, self.colorScheme['textClickable']))
        self.bind("<Button-1>", partial(self.runCommand))

    def runCommand(self, widget):
        if self.commandParameters != None:
            self.command(self.commandParameters)
        else:
            self.command()

    def color_config(self, widget, color, event):
        if not self.selected:
            widget.configure(foreground=color)

class TitleLogo(Label):
    def __init__(self, master, image, colorScheme):
        Label.__init__(self, master, bg=colorScheme['bgNormal'])
        self.image = PhotoImage(file=image)
        self.configure(image=self.image)

class TabFrame(Frame):
    def __init__(self, parent, colorScheme, tabs):
        self.parent = parent
        self.colorScheme = colorScheme # dictionary {fg1, fg2, bg, selected fg, selected bg}
        self.tabs = tabs    # list of tuples [(tabName, tabFrame), ...]
        Frame.__init__(self, self.parent, bg=self.colorScheme['bgNormal'])
        self.initUIOutline()
        self.initUI()
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

    def initUIOutline(self):
        self.buttonFrame = Frame(self, bg=self.colorScheme['bgNormal'], width=200)
        self.buttonFrame.grid(row=0, column=0, sticky='nsew')

        self.contentFrame = Frame(self, bg=self.colorScheme['bgSecondary'])
        self.contentFrame.grid(row=0, column=1, sticky='nsew', ipadx=5, ipady=5)

    def initUI(self):
        self.tabButtons = [TabButton(self.buttonFrame, item[0], self.colorScheme, self.changeTabs, item[1], 20, 2) for i, item in enumerate(self.tabs)]
        for i, item in enumerate(self.tabButtons):
            item.grid(row=i, column=0, sticky='nsew')

        self.changeTabs(self.tabButtons[0])

    def changeTabs(self, tabButton):
        for item in self.tabButtons:
            item.drawButton()

        tabButton.configure(fg=self.colorScheme['textSelected'], bg=self.colorScheme['bgSecondary'])
        tabButton.unbind_all(['<Enter>', '<Leave>', '<Button-1>'])
        tabButton.selected = True
        sensorNum = tabButton.text.split(' ')[-1]
        if not sensorNum.isdigit():
            sensorNum = '0'
        self.changeContentFrame(tabButton.contentFrame, int(sensorNum))

    def changeContentFrame(self, displayFrame, sensor):
        if hasattr(self, 'currentFrame'):
            self.currentFrame.kill()
            self.currentFrame.pack_forget()
        self.currentFrame = displayFrame(self.contentFrame, sensor)
        self.currentFrame.pack(side=TOP, fill=BOTH, expand=1, padx=10, pady=10)

    def kill(self):
        self.currentFrame.kill()

class TabButton(LinkButton):
    def __init__(self, master, text, colorScheme, command, contentFrame, width, height):
        self.contentFrame = contentFrame
        self.colorScheme = colorScheme
        self.command = command
        self.text = text
        LinkButton.__init__(self, master, self.text, self.command, self.colorScheme, width=width, height=height)
        self.drawButton()

    def runCommand(self, widget):
        self.command(self)

class GraphContainer(object):
    def __init__(self, graphNumber, canvas, toolbar):
        self.graphNumber = graphNumber
        self.canvas = canvas
        self.toolbar = toolbar
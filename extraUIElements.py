
__author__ = 'Adam Carlson'

from tkinter import Frame, Label, PhotoImage
from functools import partial


class LinkButton(Label):
    def __init__(self, master, text, command, colorScheme):
        Label.__init__(self, master, text=text)
        self.colorScheme = colorScheme
        self.command = command
        self.text = text
        self.drawButton()

    def drawButton(self):
        self.config(fg=self.colorScheme['fg1'], bg=self.colorScheme['bg'], font=("Calibri", 16))
        self.bind("<Enter>", partial(self.color_config, self, self.colorScheme['fg2']))
        self.bind("<Leave>", partial(self.color_config, self, self.colorScheme['fg1']))
        self.bind("<Button-1>", partial(self.runCommand))

    def runCommand(self, widget):
        self.command()

    def color_config(self, widget, color, event):
        widget.configure(foreground=color)

class TitleLogo(Label):
    def __init__(self, master, image):
        Label.__init__(self, master, bg='#3B3B3B')
        self.image = PhotoImage(file=image)
        self.configure(image=self.image)

class TabFrame(Frame):
    def __init__(self, parent, colorScheme, tabs):
        self.parent = parent
        self.colorScheme = colorScheme # dictionary {fg1, fg2, bg, selected fg, selected bg}
        self.tabs = tabs    # list of tuples [(tabName, tabFrame), ...]
        Frame.__init__(self, self.parent)
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
        self.tabButtons = [TabButton(self.buttonFrame, text, self.colorScheme, self.changeTabs, frame) for i, (text, frame) in enumerate(self.tabs)]
        for i, item in enumerate(self.tabButtons):
            item.grid(row=i, column=0, sticky='nw')

        self.changeTabs(self.tabButtons[0])

    def changeTabs(self, tabButton):
        for item in self.tabButtons:
            item.drawButton()

        tabButton.configure(fg=self.colorScheme['selected fg'], bg=self.colorScheme['selected bg'])
        tabButton.unbind_all(['<Enter>', '<Leave>', '<Button-1>'])
        sensorNum = tabButton.text.split(' ')[-1]
        if sensorNum.isdigit():
            self.changeContentFrame(tabButton.contentFrame, int(sensorNum))
        else:
            self.changeContentFrame(tabButton.contentFrame, 0)

    def changeContentFrame(self, frame, sensor=0):
        self.currentFrame.grid_remove()
        if sensor > 0:
            self.currentFrame = frame(self.contentFrame, sensor)
        else:
            self.currentFrame = frame(self.contentFrame)
        self.grid(row=0, column=0, sticky='nw')

class TabButton(LinkButton):
    def __init__(self, master, text, colorScheme, command, frame):
        self.contentFrame = frame
        self.colorScheme = colorScheme
        self.command = command
        self.text = text
        LinkButton.__init__(self, master, self.text, self.command, self.colorScheme)
        self.drawButton()

    def runCommand(self, widget):
        self.command(self)

__author__ = 'Adam Carlson'

from tkinter import Frame, Label, PhotoImage
from tkinter import TOP, BOTH
from functools import partial


class LinkButton(Label):
    def __init__(self, master, text, command, colorScheme, **kwargs):
        self.commandParameters = kwargs.pop('commandParameters', None)
        Label.__init__(self, master, kwargs, text=text)
        self.colorScheme = colorScheme
        self.command = command
        self.text = text
        self.drawButton()

    def drawButton(self):
        self.selected = False
        self.config(fg=self.colorScheme['textClickable'], bg=self.colorScheme['bgNormal'], font=("Calibri", 16))
        self.bind("<Enter>", partial(self.color_config, self, self.colorScheme['textHover']))
        self.bind("<Leave>", partial(self.color_config, self, self.colorScheme['textClickable']))
        self.bind("<Button-1>", self.runCommand)

    def runCommand(self, widget):
        if self.commandParameters != None:
            self.command(self.commandParameters)
        else:
            self.command()

    def color_config(self, widget, fg, event):
        if not self.selected:
            widget.configure(fg=fg)

class RecentFilesList(Frame):
    def __init__(self, parent, settingsObject, colorScheme):
        Frame.__init__(self, parent, bg=colorScheme['bgNormal'])
        self.settingsObject = settingsObject
        self.parent = parent
        self.colorScheme = colorScheme
        self.initUI()

    def initUI(self):
        for i, item in enumerate(self.settingsObject.filePaths):
            LinkButton(self, item.split('.')[0].split('/')[-1],self.open,
                       self.colorScheme, commandParameters=item).grid(row=i, sticky='nw', padx=40)

    def open(self, filePath):
        self.settingsObject.root.fOpen(filePath)

class QuickSelectList(Frame):
    def __init__(self, parent, settingsObject, colorScheme):
        Frame.__init__(self, parent, bg=colorScheme['bgNormal'])
        self.settingsObject = settingsObject
        self.colorScheme = colorScheme
        self.initUI()

    def initUI(self):
        for i, item in enumerate(self.settingsObject.get_quick_files()):
            item = item.replace('\\', '/')
            LinkButton(self, item.split('/')[-1],self.open,
                       self.colorScheme, commandParameters=item).grid(row=i, sticky='nw', padx=40)

    def open(self, filename):
        self.settingsObject.root.fImportData(filename)


class ToggleButton(Label):
    def __init__(self, parent, command, colorScheme, **kwargs):
        self.commandParameters = kwargs.pop('commandParameters', None)
        self.on = kwargs.pop('pressed', True)
        self.dcCommand = kwargs.pop('dcCommand', command)
        self.dcCommandParameters = kwargs.pop('dcCommandParameters', self.commandParameters)
        self.textColor = kwargs.pop('textColor', colorScheme['textNormal'])
        self.parent = parent
        self.command = command
        self.colorScheme = colorScheme
        Label.__init__(self, self.parent, kwargs)
        self.drawButton()

    def drawButton(self):
        self.config(font=("Calibri", 16))
        self.config(fg=self.colorScheme['graphFg'], bg=self.colorScheme['graphBg'])
        self.bind("<Button-1>", self.runClick)
        if self.dcCommand is not None:
            self.bind("<Double-Button-1>", self.runDoubleClick)
            self.pressed = False
        self.runClick(None)
        if not self.on:
            self.runClick(None)

    def unSelect(self):
        self.pressed = False
        self.config(fg=self.colorScheme['graphFg'], bg=self.colorScheme['graphBg'])
        self.bind("<Enter>", partial(self.color_config, self, self.textColor))
        self.bind("<Leave>", partial(self.color_config, self, self.colorScheme['graphFg']))

    def select(self):
        self.pressed = True
        self.config(fg=self.textColor, bg=self.colorScheme['bgNormal'])
        self.unbind_all(['<Enter>', '<Leave>'])

    def runClick(self, event):
        if self.pressed:
            self.unSelect()
        else:
            self.select()

        if self.commandParameters is not None:
            self.command(self, self.commandParameters)
        else:
            self.command(self)

    def runDoubleClick(self, event):
        if self.pressed:
            if self.dcCommandParameters is not None:
                self.dcCommand(self, self.dcCommandParameters)
            else:
                self.dcCommand(self)
        else:
            self.runClick(None)
            if self.dcCommandParameters is not None:
                self.dcCommand(self, self.dcCommandParameters)
            else:
                self.dcCommand(self)

    def color_config(self, widget, color, event):
        if not self.pressed:
            widget.configure(foreground=color)

class ToggleButtonFrame(Frame):
    def __init__(self, parent, figureClass, sensorData, colorScheme):
        self.parent = parent
        self.figureClass = figureClass
        self.sensorData = sensorData
        self.colorScheme = colorScheme
        Frame.__init__(self, parent)

        for i in range(5):
            self.columnconfigure(i*2, weight=1)

        self.initUI()

    def initUI(self):

        for i in range(8):
            if i % 2 == 1:
                Frame(self, width=2, bg=self.colorScheme['bgSecondary']).grid(row=0, column=i, sticky='nsew')


        LinkButton(self, 'Show All', self.show_all, self.colorScheme).grid(row=0, column=0, sticky='nsew')

        self.xButton = ToggleButton(self, self.singleClickCommand, self.colorScheme, text='X Axis',
                                    textColor=self.colorScheme['graphX'], commandParameters='X',
                                    dcCommand=self.doubleClickCommand, height=1, pressed=self.figureClass.toggled[0])
        self.xButton.grid(row=0, column=2, sticky='nsew')

        self.yButton = ToggleButton(self, self.singleClickCommand, self.colorScheme, text='Y Axis',
                                    textColor=self.colorScheme['graphY'], commandParameters='Y',
                                    dcCommand=self.doubleClickCommand, height=1, pressed=self.figureClass.toggled[1])
        self.yButton.grid(row=0, column=4, sticky='nsew')

        self.zButton = ToggleButton(self, self.singleClickCommand, self.colorScheme, text='Z Axis',
                                    textColor=self.colorScheme['graphZ'], commandParameters='Z',
                                    dcCommand=self.doubleClickCommand, height=1, pressed=self.figureClass.toggled[2])
        self.zButton.grid(row=0, column=6, sticky='nsew')

        LinkButton(self, 'Add Filter', self.sensorData.filter, self.colorScheme).grid(row=0, column=8, sticky='nsew')

    def show_all(self):
        self.figureClass.show_all()
        self.xButton.select()
        self.yButton.select()
        self.zButton.select()

    def singleClickCommand(self, button, identifier):
        if button.pressed:
            self.figureClass.showSubplot(identifier)
        else:
            self.figureClass.hideSubplot(identifier)

    def doubleClickCommand(self, button, identifier):
        plots = ['X', 'Y', 'Z']
        buttons = [self.xButton, self.yButton, self.zButton]
        for i, item in enumerate(plots):
            if item != identifier:
                buttons[i].unSelect()
                self.figureClass.hideSubplot(item)

    def kill(self):
        newToggled = (self.xButton.pressed, self.yButton.pressed, self.zButton.pressed)
        if self.figureClass.toggled != newToggled:
            self.figureClass.toggled = newToggled
            self.sensorData.saved[1] = False


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
        Frame.__init__(self, self.parent, bg=self.colorScheme['bgSecondary'])
        self.initUIOutline()
        self.initUI()
        self.columnconfigure(2, weight=1)
        self.rowconfigure(0, weight=1)

    def initUIOutline(self):
        self.buttonFrame = Frame(self, bg=self.colorScheme['bgNormal'], width=200)
        self.buttonFrame.grid(row=0, column=0, sticky='nsew')

        Frame(self, bg=self.colorScheme['bgSecondary'], width=5).grid(row=0, column=1, sticky='nsew')

        self.contentFrame = Frame(self, bg=self.colorScheme['bgSecondary'])
        self.contentFrame.grid(row=0, column=2, sticky='nsew')# ipadx=5, ipady=5)

    def initUI(self):
        self.tabButtons = [TabButton(self.buttonFrame, item[0], self.colorScheme, self.changeTabs, item[1], 20, 2) for i, item in enumerate(self.tabs)]
        for i, item in enumerate(self.tabButtons):
            item.grid(row=i, column=0, sticky='nsew')

        self.changeTabs(self.tabButtons[1])

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
        self.currentFrame.pack(side=TOP, fill=BOTH, expand=1)#, padx=10, pady=10)

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

    def drawButton(self):
        self.selected = False
        self.config(fg=self.colorScheme['textClickable'], bg=self.colorScheme['bgNormal'], font=("Calibri", 16))
        self.bind("<Enter>", partial(self.color_config, self, self.colorScheme['textHover']))
        self.bind("<Leave>", partial(self.color_config, self, self.colorScheme['textClickable']))
        self.bind("<Button-1>", self.runCommand)

    def runCommand(self, widget):
        self.command(self)

class GraphContainer(object):
    def __init__(self, graphNumber, canvas, toolbar):
        self.graphNumber = graphNumber
        self.canvas = canvas
        self.toolbar = toolbar
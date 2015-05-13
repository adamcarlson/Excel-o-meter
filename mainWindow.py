__author__ = 'Adam Carlson'


import matplotlib
matplotlib.use('TkAgg')

from tkinter import messagebox
from tkinter import *
from fixedCanvasToolbar import ActuallyWorkingFigureCanvas, ActuallyWorkingToolbar
from extraUIElements import TabFrame, TitleLogo, LinkButton, ToggleButtonFrame
from extraUIElements import RecentFilesList, QuickSelectList
import sensorData as sd
from settingsContainer import Settings
from os import path

# Constants:
FRAME, CANVAS, TOOLBAR = 0, 1, 2
gX, gY, gZ = 0, 1, 2

colors = {
    'textClickable' : '#0088FF',
    'textHover' : '#00D5FF',
    'textNormal' : '#D9D9D9',
    'textSelected' : '#00D5FF',     # Usually the same as textHover

    'bgNormal': '#3B3B3B',
    'bgSecondary' : '#2B2B2B',
    'textField' : '#D9D9D9',

    'graphBg' : '#D9D9D9',
    'graphFg' : 'black',
    'graphX' : 'blue',
    'graphY' : 'green',
    'graphZ' : 'red',
}


class MainApp(Tk):
    def __init__(self):
        Tk.__init__(self)
        self.protocol("WM_DELETE_WINDOW", self.fOnExit)
        if path.isfile('settings.dat'):
            self.recentFiles = Settings(self, filename='settings.dat')
        else:
            self.recentFiles = Settings(self)

        self.makeMenuBar()

    def run(self):
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
        fileMenu.add_separator()
        fileMenu.add_command(label="Save As...", command=self.fSaveAs)
        fileMenu.add_command(label="Save", command=self.fSave)
        fileMenu.add_separator()
        fileMenu.add_command(label='Export to .xlsx', command=self.fExport)
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
        self.currentFrame.kill()
        self.currentFrame.pack_forget()
        self.currentFrame.destroy()
        self.currentFrame = newFrame(self)
        self.currentFrame.pack(side=TOP, fill=BOTH, expand=1)

    def showSaveDialogue(self):
        return messagebox.askyesno("Excelometer", "Unsaved changes have been made."
                                                  "\nWould you like to save before exiting?")
    def save_if_needs_saving(self):
        self.currentFrame.kill()
        if sensorData.saved[1] == False:
            if(self.showSaveDialogue()):
                self.fSave()

    #File Menu
    def fImportData(self, filename=''):
        self.save_if_needs_saving()
        sensorData.importData(filename)
        self.recentFiles.lastFolderPath = '/'.join(sensorData.filename.split('/')[:-1])
        print(self.recentFiles.lastFolderPath)
        self.changeFrame(RunView)

    def fOpen(self, filename=''):
        self.save_if_needs_saving()
        sensorData.newData(sd.openSaveFile(self.recentFiles, filename))
        self.changeFrame(RunView)

    def fSaveAs(self):
        sd.saveFile(sensorData, self.recentFiles)

        if hasattr(self.currentFrame, 'runTitle'):
            self.currentFrame.runTitle.config(text=sensorData.runData['runTitle'])

    def fSave(self):
        if sensorData.saved[0] == False:
            self.fSaveAs()
        elif sensorData.saved[1] == False:
            sd.saveFile(sensorData, self.recentFiles, sensorData.runData['runFileLocation'])

    def fOnExit(self):
        self.save_if_needs_saving()
        self.recentFiles.save_settings()
        sys.exit()

    def fExport(self):
        sd.export_options(sensorData, colors)

    #Edit Menu
    def eFilter(self):
        sensorData.filter()

    # Help Menu
    def hHelp(self):
        pass

class HomeWindow(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent, bg=colors['bgNormal'])
        self.parent = parent
        self.parent.resizable(0, 0)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(2, weight=1)
        self.rowconfigure( 3, weight=1)
        self.initUI()

    def initUI(self):
        self.parent.title("Excelometer - Start Page")

        TitleLogo(self, 'elogo.png', colors).grid(row=0, column=0, columnspan=3)

        lineFrameH1 = Frame(self, bg=colors['bgSecondary'], height=2, width=1000)
        lineFrameH1.grid(row=1, column=0, columnspan=3, sticky='nsew')

        lineFrameV1 = Frame(self, bg=colors['bgSecondary'], height=500, width=2)
        lineFrameV1.grid(row=2, column=1, rowspan=2, sticky='nsew')

        startFrame = Frame(self, bg=colors['bgNormal'])
        startFrame.grid(row=2, column=0, sticky='nsew')

        quickSelectFrame = Frame(self, bg=colors['bgNormal'])
        quickSelectFrame.grid(row=2, column=2, rowspan=2, sticky='nsew')

        recentsFrame = Frame(self, bg=colors['bgNormal'])
        recentsFrame.grid(row=3, column=0, padx=2, pady=10, sticky='nsew')

        Label(startFrame, text="Start", font=("Calibri", 20), bg=colors['bgNormal'], fg=colors['textNormal']).grid(row=0, sticky='nw', padx=40, pady=5)

        importButton = LinkButton(startFrame, "Import data...", self.parent.fImportData, colors)
        importButton.grid(row=1, sticky='w', padx=40)
        openButton = LinkButton(startFrame, "Open...", self.parent.fOpen, colors)
        openButton.grid(row=2, sticky='w', padx=40)

        Label(recentsFrame, text="Recents", font=("Calibri", 20), bg=colors['bgNormal'], fg=colors['textNormal']).grid(row=0, sticky='nw', padx=40, pady=5)
        RecentFilesList(recentsFrame, self.parent.recentFiles, colors).grid(row=1, sticky='nw')

        Label(quickSelectFrame, text="Quick Select", font=("Calibri", 20), bg=colors['bgNormal'], fg=colors['textNormal']).grid(row=0, sticky='nw', padx=40, pady=5)
        QuickSelectList(quickSelectFrame, self.parent.recentFiles, colors).grid(row=1, sticky='nw')

    def kill(self):
        pass

class RunView(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent, bg=colors['bgNormal'])
        self.parent = parent
        self.parent.geometry('1500x800')
        self.parent.resizable(1, 1)
        self.descriptionText = ''
        self.initUI()
        self.columnconfigure(2, weight=1)
        self.rowconfigure(3, weight=1)

    def initUI(self):
        self.parent.title("Excelometer - {}".format(sensorData.runData['runTitle']))

        logoFrame = Frame(self, bg=colors['bgNormal'], width=231)
        logoFrame.grid(row=0, column=0, rowspan=3, sticky='nsew')
        self.logo = PhotoImage(file='eomIcon.PNG')
        Label(logoFrame, bg=colors['bgNormal'], image=self.logo, width=227).pack(side=TOP, fill=BOTH, expand=0)
        Frame(self, bg=colors['bgSecondary'], width=5).grid(row=0, column=1, rowspan=3, sticky='nsew')

        self.runTitle = Label(self, text=sensorData.runData['runTitle'], fg=colors['textNormal'], bg=colors['bgNormal'], height=1, font=("Calibri", 30))
        self.runTitle.grid(row=0, column=2, sticky='nw', columnspan=2, ipadx=10)

        lineFrameH1 = Frame(self, bg=colors['bgSecondary'], height=2)
        lineFrameH1.grid(row=1, column=2, columnspan=2, sticky='new')

        timeLabel = Label(self, text='Run Durration: {}'.format(sensorData.runData['runTime']), fg=colors['textNormal'], bg=colors['bgNormal'], font=("Calibri", 16))
        timeLabel.grid(row=2, column=2, sticky='nsw', ipadx=10)
        dateLabel = Label(self, text=sensorData.runData['runDate'], fg=colors['textNormal'], bg=colors['bgNormal'], font=("Calibri", 16))
        dateLabel.grid(row=2, column=3, sticky='nse', ipadx=10)

        tabs = [('Notes', NoteView)]
        for i in range(sensorData.numberOfSensors):
            tabs.append(('Sensor {}'.format(i+1), SensorView))

        self.contentFrame = Frame(self, bg=colors['bgSecondary'])
        self.contentFrame.grid(row=3, column=0, sticky='nsew', columnspan=4)

        self.content = TabFrame(self.contentFrame, colors, tabs)
        self.content.pack(side=TOP, fill=BOTH, expand=1, padx=5, pady=5)
        #self.content.grid(row=3, column=0, sticky='nsew', columnspan=3, padx=10, pady=10)

    def kill(self):
        self.content.kill()

class NoteView(Frame):
    def __init__(self, parent, junk=0):
        self.parent = parent
        Frame.__init__(self, self.parent, bg=colors['bgNormal'])
        self.initUI()

    def initUI(self):
        self.descriptionBox = Text(self, width=124, height=20, bg=colors['textField'])
        self.descriptionBox.insert(END, sensorData.runData['runNotes'][:-1])
        self.descriptionBox.pack(side=TOP, fill=BOTH, expand=1)

    def kill(self):
        if sensorData.runData['runNotes'] != self.descriptionBox.get('1.0', END):
            sensorData.runData['runNotes'] = self.descriptionBox.get('1.0', END)
            sensorData.saved[1] = False

class SensorView(Frame):
    def __init__(self, parent, sensor, tabFrame):
        self.parent = parent
        self.sensorNum = sensor - 1
        self.tabFrame = tabFrame
        Frame.__init__(self, self.parent, bg=colors['bgSecondary'])
        self.initUI()
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

    def initUI(self):
        self.canvas = ActuallyWorkingFigureCanvas(sensorData.plotList[self.sensorNum].figure, self)
        self.toolbar = ActuallyWorkingToolbar(self.canvas, self)
        sensorData.grabHistory(self.sensorNum, self.toolbar._views, self.toolbar._positions)
        sensorData.setHistory(self.sensorNum, self.toolbar)

        self.canvas.show()
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky='nsew')
        self.canvas.get_tk_widget().configure(bg=colors['graphBg'], highlightthickness=0)

        self.toolbar.frame.grid(row=1, column=0, sticky='nsew', ipadx=1)
        self.toolbar.frame.configure(bg=colors['graphBg'])
        self.toolbar.configure(bg=colors['graphBg'])
        self.toolbar._message_label.configure(bg=colors['graphBg'])

        Frame(self, height=5, bg=colors['bgSecondary']).grid(row=2, column=0, sticky='nsew')

        self.buttons = ToggleButtonFrame(self, sensorData.plotList[self.sensorNum], sensorData, colors)
        self.buttons.grid(row=3, column=0, sticky='nsew')

    def changePlot(self, plot):
        pass

    def filterGraph(self):
        popup = Tk()
        popup.title('Moving Average Vector Length')
        sd.FilterWindow(popup, sensorData, colors, self).pack()
        sensorData.saved[1] = False

    def kill(self):
        self.buttons.kill()








if __name__ == '__main__':
    sensorData = sd.SensorData(colors)
    app = MainApp()
    app.run()
    app.mainloop()
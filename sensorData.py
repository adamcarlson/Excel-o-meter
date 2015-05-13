__author__ = 'Adam Carlson'


import tkinter.filedialog as fd
import numpy as np
from subprocess import Popen, PIPE
import matplotlib.pyplot as plt
import os
from datetime import datetime, timedelta
import pickle
import xlsxwriter
from tkinter import Tk, Frame, Label, Scale, HORIZONTAL
from tkinter import NORMAL, DISABLED, StringVar, IntVar, OptionMenu, TOP, BOTH, X
from math import pow
from extraUIElements import TabButton, ToggleButton, LinkButton

class SensorData(object):
    def __init__(self, colorScheme, numberOfSensors = 3, Hz=800):
        self.interval = 1/Hz
        self.numberOfSensors = numberOfSensors
        self.colorScheme = colorScheme
        self.saved = [False, True]     # [been saved before, currently saved]
        self.runData = {}

    def importData(self, filename=''):
        if filename is '':
            self.filename = fd.askopenfilename(filetypes=[('Excel-o-meter Data Dump File','*.sac')])
            self.runData['runTitle'] = self.filename.split('.')[0].split('/')[-1]
        else:
            self.filename = filename
            self.runData['runTitle'] = self.filename.split('.')[0].split('\\')[-1]
        if self.filename.split('.')[-1] == 'sac':
            self.numberOfSensors = self.runUnpacker(self.filename)
            record_dtype = np.dtype([('x_data', np.float32), ('y_data', np.float32), ('z_data', np.float32)])
            temp = [(np.fromfile('s{}.dat'.format(i), dtype=record_dtype), os.remove('s{}.dat'.format(i)))[0] for i in range(self.numberOfSensors)]
            self.data = [[temp[i]['x_data'], temp[i]['y_data'], temp[i]['z_data']] for i in range(self.numberOfSensors)]

            self.truncateToShortest()
            self.t = np.arange(0.0,(self.intervalCount*self.interval),self.interval)

            self.plotList = [FigurePlot(item, self.t, self.colorScheme) for item in self.data]

            self.runData['runFileLocation'] = self.runData['runTitle'] + '.esf'
            self.runData['runTime'] = str(timedelta(milliseconds=(self.intervalCount * self.interval)))
            self.runData['runDate'] = datetime.now().strftime('%Y-%m-%d')
            self.runData['runTimeMS'] = self.intervalCount * self.interval
            self.runData['runNotes'] = ''
            self.saved[1] = False

    def runUnpacker(self, filename):
        process = Popen([r"eom.exe", "{}".format(filename)], stdout=PIPE)
        stdout, stderr = process.communicate()
        process.wait()
        return int(stdout.decode())

    def newData(self, sensorDataObject):
        self.data = sensorDataObject.data
        self.interval = sensorDataObject.interval
        self.numberOfSensors = sensorDataObject.numberOfSensors
        self.intervalCount = sensorDataObject.intervalCount
        self.plotList = sensorDataObject.plotList
        self.runData = sensorDataObject.runData
        self.saved = [True, True]

    def grabHistory(self, sensor, view, position):
        if 'runHistory{}'.format(sensor) not in self.runData.keys():
            self.runData['runHistory{}'.format(sensor)] = (view, position)

    def setHistory(self, sensor, toolbar):
        toolbar._views, toolbar._positions = self.runData['runHistory{}'.format(sensor)]
        toolbar.set_history_buttons()
        toolbar._update_view()

    # Utility Methods
    def truncateToShortest(self):
        count = self.smallestSize()
        for sensor, item in enumerate(self.data):
            self.data[sensor] = [item[i][0:count] for i in range(3)]

    def smallestSize(self):
        count = 0
        for sensor in self.data:
            for item in sensor:
                size = np.size(item)
                if count == 0 or size < count:
                    count = size
        self.intervalCount = count
        return self.intervalCount

    def filter(self, N):
        for item in self.plotList:
            for i, axis in enumerate(item.axisList):
                item.axisList[i] = runningMean(axis, N)
            item.makePlots()

def runningMean(x, N):
    return np.convolve(x, np.ones((N,))/N)[(N-1):]

class FigurePlot(object):
    def __init__(self, axisList, t, colorScheme):
        self.originalAxisList = axisList
        self.axisList = axisList
        self.t = t
        self.colorScheme = colorScheme
        self.makePlots()
        self.toggled = (1,1,1)

    def makePlots(self):
        self.figure = plt.figure(figsize=(1,1), dpi=100, frameon=False, facecolor=self.colorScheme['graphBg'])
        self.AxisPlot = self.figure.add_axes([.06, .1, .88, .8])
        self.AxisPlot.set_xlabel(r'thousands of samples')
        self.AxisPlot.set_ylabel(r"g's")
        self.lines = self.AxisPlot.plot(self.t, self.axisList[0], self.colorScheme['graphX'],
                                        self.t, self.axisList[1], self.colorScheme['graphY'],
                                        self.t, self.axisList[2], self.colorScheme['graphZ'])

    def reload_plot(self):
        self.lines = self.AxisPlot.plot(self.t, self.axisList[0], self.colorScheme['graphX'],
                                        self.t, self.axisList[1], self.colorScheme['graphY'],
                                        self.t, self.axisList[2], self.colorScheme['graphZ'])

    def hideSubplot(self, identifier):
        if identifier == 'X':
            self.lines[0].set_visible(False)
        elif identifier == 'Y':
            self.lines[1].set_visible(False)
        elif identifier == 'Z':
            self.lines[2].set_visible(False)

        self.figure.canvas.draw()

    def showSubplot(self, identifier):
        if identifier == 'X':
            self.lines[0].set_visible(True)
        elif identifier == 'Y':
            self.lines[1].set_visible(True)
        elif identifier == 'Z':
            self.lines[2].set_visible(True)

        self.figure.canvas.draw()

    def show_all(self):
        for item in self.lines:
            item.set_visible(True)

        self.figure.canvas.draw()


#------------------------ External Functions ---------------------------------------------

def openSaveFile(recentsObject, filename=''):
    if filename == '':
        ofFileName = fd.askopenfilename(filetypes=[('Excel-o-meter Save File','*.esf')])
        file = open(ofFileName, 'rb')
    else:
        ofFileName = filename
        file = open(ofFileName, 'rb')

    sensorDataObject = pickle.Unpickler(file).load()
    file.close()
    recentsObject.add_recent(ofFileName)
    return(sensorDataObject)

def saveFile(sensorDataObject, recentsObject, filename=''):
    if filename == '':
        sfFileName = fd.asksaveasfilename(filetypes=[("Excelometer Save Files", "*.esf" ),("All files", "*")], defaultextension='.esf')
        file = open(sfFileName, 'wb')
        sensorDataObject.runData['runFileLocation'] = sfFileName
        sensorDataObject.runData['runTitle'] = sfFileName.split('.')[0].split('/')[-1]
    else:
        sfFileName = filename
        file = open(sfFileName, 'wb')

    sensorDataObject.saved = [True, True]
    pickle.Pickler(file).dump(sensorDataObject)
    file.close()
    recentsObject.add_recent(sfFileName)
    return

def export_to_xlsx(sensorDataObject, sensors, frequency, filtered):
    filename = fd.asksaveasfilename(filetypes=[("Excel Workbook", "*.xlsx" ),("All files", "*")], defaultextension='.xlsx')

    workbook = xlsxwriter.Workbook(filename)
    bold = workbook.add_format({'bold' : 1})

    for sensor, figurePlotObject in enumerate(sensorDataObject.plotList):
        if sensors[sensor]:
            worksheet = workbook.add_worksheet('Sensor {}'.format(sensor+1))
            worksheet.write('A1', 'X axis', bold)
            worksheet.write('B1', 'Y axis', bold)
            worksheet.write('C1', 'Z axis', bold)
            if filtered:
                axisList = figurePlotObject.axisList
            else:
                axisList = figurePlotObject.originalAxisList
            for column, axis in enumerate(axisList):
                newAxis = convert_to_lower_frequency(axis, int(frequency.split()[0]))
                for row, dataPoint in enumerate(newAxis):
                    worksheet.write_number(row+1, column, dataPoint)
    workbook.close()

def convert_to_lower_frequency(array, frequency):
    if frequency == 800:
        return array
    else:
        if len(array) % 2 == 1:
            array.append([array[-1]])
        return convert_to_lower_frequency([(array[i] + array[i+1]) / 2 for i in range(len(array)) if  i%2 == 0], frequency*2)

def export_options(sensorDataObject, colorScheme):
    popup = Tk()
    popup.title('Export...')
    ExportWindow(popup, sensorDataObject, colorScheme).pack(side=TOP, fill=BOTH, expand=1)


class ExportWindow(Frame):
    def __init__(self, parent, sensorDataObject, colorScheme):
        Frame.__init__(self, parent)
        self.sensorDataObject = sensorDataObject
        self.parent = parent
        self.parent.resizable(0,0)
        self.colorScheme = colorScheme
        self.configure(bg=self.colorScheme['bgNormal'])
        self.initUI()

    def initUI(self):

        Label(self, text='Exporting as .xlsx', bg=self.colorScheme['bgNormal'], fg=self.colorScheme['textNormal'], font=("Calibri", 16)).grid(row=0, column=0, sticky='nsew')

        Label(self, text='Sensors:', bg=self.colorScheme['bgNormal'], fg=self.colorScheme['textNormal'], font=("Calibri", 16)).grid(row=2, column=0, sticky='nsew')
        Label(self, text='Frequency:', bg=self.colorScheme['bgNormal'], fg=self.colorScheme['textNormal'], font=("Calibri", 16)).grid(row=2, column=2, sticky='nsew')

        leftRadioButtons = Frame(self, bg=self.colorScheme['bgNormal'])
        leftRadioButtons.grid(row=4, column=0, sticky='nsew')

        lineFrameH2 = Frame(self, bg=self.colorScheme['bgSecondary'], height=4, width=300)
        lineFrameH2.grid(row=3, column=0, columnspan=3, sticky='nsew')

        lineFrameH1 = Frame(self, bg=self.colorScheme['bgSecondary'], height=4, width=300)
        lineFrameH1.grid(row=1, column=0, columnspan=3, sticky='nsew')

        lineFrameV2 = Frame(self, bg=self.colorScheme['bgSecondary'], height=100, width=4)
        lineFrameV2.grid(row=4, column=1, rowspan=3, sticky='nsew')

        lineFrameV1 = Frame(self, bg=self.colorScheme['bgSecondary'], height=1, width=4)
        lineFrameV1.grid(row=2, column=1, rowspan=1, sticky='nsew')

        rightRadioButtons = Frame(self, bg=self.colorScheme['bgNormal'])
        rightRadioButtons.grid(row=4, column=2, rowspan=2)

        tabsLeft = [("All", NullFrame), ("Select", SensorSelect)]
        tabsRight = [("{} Hz".format(int(100*pow(2,3-i))), NullFrame) for i in range(4)]

        self.tbLeft = [TabButton(leftRadioButtons, tabsLeft[i][0], self.colorScheme, self.change_tabs, tabsLeft[i][1], 16, 2) for i in range(2)]
        for i, item in enumerate(self.tbLeft):
            item.grouping = "left"
            item.grid(row=i*2, column=0, sticky='nw')

        for i in range(4):
            if i % 2 == 1:
                Frame(leftRadioButtons, height=2, bg=self.colorScheme['bgSecondary']).grid(row=i, column=0, sticky='nsew')


        self.tbRight = [TabButton(rightRadioButtons, tabsRight[i][0], self.colorScheme, self.change_tabs, tabsRight[i][1], 16, 2) for i in range(4)]
        for i, item in enumerate(self.tbRight):
            item.grouping = "right"
            item.grid(row=i*2, column=0, sticky='nw')

        for i in range(8):
            if i % 2 == 1:
                Frame(rightRadioButtons, height=2, bg=self.colorScheme['bgSecondary']).grid(row=i, column=0, sticky='nsew')

        self.toggleFrame = Frame(self, bg=self.colorScheme['bgSecondary'])
        self.toggleFrame.grid(row=5, column=0, sticky='new')

        self.change_tabs(self.tbLeft[0])
        self.change_tabs(self.tbRight[0])

        LinkButton(self, 'Export Original Data', self.export, self.colorScheme, commandParameters=False).grid(row=6, column=2, pady=5, sticky='nsew')
        LinkButton(self, 'Export Filtered Data', self.export, self.colorScheme, commandParameters=True).grid(row=6, column=0, pady=5, sticky='nsew')

    def change_tabs(self, tabButton):
        if tabButton.grouping == "left":
            for item in self.tbLeft:
                item.drawButton()

            tabButton.configure(fg=self.colorScheme['textSelected'], bg=self.colorScheme['bgSecondary'])
            tabButton.unbind_all(['<Enter>', '<Leave>', '<Button-1>'])
            tabButton.selected = True
            self.change_content_frame(tabButton.contentFrame)

        else:
            for item in self.tbRight:
                item.drawButton()

            tabButton.configure(fg=self.colorScheme['textSelected'], bg=self.colorScheme['bgSecondary'])
            tabButton.unbind_all(['<Enter>', '<Leave>', '<Button-1>'])
            tabButton.selected = True
            self.currentFrequency = tabButton.text

    def change_content_frame(self, displayFrame):
        if hasattr(self, 'currentFrame'):
            self.currentFrame.kill()
            self.currentFrame.pack_forget()
        self.currentFrame = displayFrame(self.toggleFrame, self.colorScheme, self.sensorDataObject)
        self.currentFrame.pack(side=TOP, fill=BOTH, expand=1)

    def export(self, filtered):
        if self.tbLeft[0].selected:
            sensors = [True for i in range(self.sensorDataObject.numberOfSensors)]
        else:
            sensors = [button.selected for button in self.currentFrame.buttons]

        export_to_xlsx(self.sensorDataObject, sensors, self.currentFrequency, filtered)

        self.parent.destroy()

class SensorSelect(Frame):
    def __init__(self, parent, colorScheme, sensorDataObject):
        Frame.__init__(self, parent, bg=colorScheme['bgNormal'])
        self.colorScheme = colorScheme
        self.sensorDataObject = sensorDataObject
        self.toggler = Toggle()
        self.initUI()

    def initUI(self):
        buttons = [("Sensor {}".format(i+1), NullFrame) for i in range(self.sensorDataObject.numberOfSensors)]

        while len(buttons) < 3:
            buttons.append(("", NullFrame))

        self.buttons = [TabButton(self, buttons[i][0], self.colorScheme, self.sensor_click, buttons[i][0], 16, 1) for i in range(3)]
        for i, item in enumerate(self.buttons):
            item.grid(row=i*2, column=0, sticky='nsew', ipady=3)

        for i in range(6):
            if i % 2 == 1:
                if i/2 < self.sensorDataObject.numberOfSensors:
                    Frame(self, height=2, bg=self.colorScheme['bgSecondary']).grid(row=i, column=0, sticky='nsew')
                else:
                    Frame(self, height=2, bg=self.colorScheme['bgNormal']).grid(row=i, column=0, sticky='nsew')



    def sensor_click(self, button):
        if button.selected == False and button.text != '':
            button.configure(fg=self.colorScheme['textSelected'], bg=self.colorScheme['bgSecondary'])
            button.unbind_all(['<Enter>', '<Leave>', '<Button-1>'])
            button.selected = True
        else:
            button.drawButton()

    def kill(self):
        pass

class NullFrame(Frame):
    def __init__(self, parent, colorScheme, *args):
        Frame.__init__(self, parent, bg=colorScheme['bgNormal'])

    def kill(self):
        pass

class Toggle(object):
    def __init__(self):
        self.toggled = [0,0,0]

class FilterWindow(Frame):
    def __init__(self, parent, sensorDataObject, colorScheme, mainApp):
        Frame.__init__(self, parent)
        self.sensorDataObject = sensorDataObject
        self.parent = parent
        self.mainApp = mainApp
        self.parent.resizable(0,0)
        self.colorScheme = colorScheme
        self.configure(bg=self.colorScheme['bgNormal'])
        self.initUI()

    def initUI(self):
        Label(self, text='Select a moving average vector length', bg=self.colorScheme['bgNormal'], width=30, fg=self.colorScheme['textNormal'], font=("Calibri", 16)).grid(row=0, column=0, sticky='nsew')

        self.vector = Scale(self, from_=2, to=100, orient=HORIZONTAL, fg=self.colorScheme['textNormal'], bg=self.colorScheme['bgNormal'], bd=0, highlightthickness=0, activebackground=self.colorScheme['bgNormal'])
        self.vector.grid(row=1, column=0, sticky='nsew', padx=4)

        LinkButton(self, 'Filter', self.filter, self.colorScheme).grid(row=2, column=0, sticky='nsew')


    def filter(self):
        self.sensorDataObject.filter(self.vector.get())
        self.mainApp.tabFrame.changeTabs(self.mainApp.tabFrame.tabButtons[self.mainApp.sensorNum+1])
        self.parent.destroy()




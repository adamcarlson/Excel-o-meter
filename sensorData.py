__author__ = 'Adam Carlson'


import tkinter.filedialog as fd
import numpy as np
from subprocess import Popen, PIPE
import matplotlib.pyplot as plt
import os
from datetime import datetime, timedelta
import pickle

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

    def filter(self):
        pass

class FigurePlot(object):
    def __init__(self, sensorList, t, colorScheme):
        self.sensorList = sensorList
        self.t = t
        self.colorScheme = colorScheme
        self.makePlots()
        self.toggled = (1,1,1)

    def makePlots(self):
        self.figure = plt.figure(figsize=(1,1), dpi=100, frameon=False, facecolor=self.colorScheme['graphBg'])
        self.AxisPlot = self.figure.add_axes([.06, .1, .88, .8])
        self.AxisPlot.set_xlabel(r'thousands of samples')
        self.AxisPlot.set_ylabel(r"g's")
        self.lines = self.AxisPlot.plot(self.t, self.sensorList[0], self.colorScheme['graphX'],
                                        self.t, self.sensorList[1], self.colorScheme['graphY'],
                                        self.t, self.sensorList[2], self.colorScheme['graphZ'])


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
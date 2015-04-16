__author__ = 'Adam Carlson'


import tkinter.filedialog as fd
import numpy as np
from subprocess import Popen, PIPE
import matplotlib.pyplot as plt
import os
from datetime import datetime, timedelta
import pickle

class SensorData(object):
    def __init__(self, numberOfSensors = 3, Hz=800):
        self.interval = 1/Hz
        self.numberOfSensors = numberOfSensors
        self.saved = [False, True]     # [been saved before, currently saved]
        self.runData = {}

    def importData(self):
        self.filename = fd.askopenfilename(filetypes=[('Excel-o-meter Data Dump File','*.sac')])
        if self.filename.split('.')[-1] == 'sac':
            self.numberOfSensors = self.runUnpacker(self.filename)
            record_dtype = np.dtype([('x_data', np.float32), ('y_data', np.float32), ('z_data', np.float32)])
            temp = [(np.fromfile('s{}.dat'.format(i), dtype=record_dtype), os.remove('s{}.dat'.format(i)))[0] for i in range(self.numberOfSensors)]
            self.data = [[temp[i]['x_data'], temp[i]['y_data'], temp[i]['z_data']] for i in range(self.numberOfSensors)]

            self.truncateToShortest()
            self.t = np.arange(0.0,(self.intervalCount*self.interval),self.interval)

            self.plotList = [self.generatePlots(item) for item in self.data]

            self.runData['runTitle'] = self.filename.split('.')[0].split('/')[-1]
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

    def generatePlots(self, sensorList):
        axis = ['X', 'Y', 'Z']
        plotList = [plt.figure(figsize=(1,1), dpi=100, frameon=False) for i in range(3)]
        for i, item in enumerate(plotList):
            plot = plotList[i].add_subplot(111)
            plot.set_xlabel(r'$samples$')
            plot.set_title('{} Axis'.format(axis[i]))
            plot.set_ylabel(r"g's")
            plot.plot(self.t, sensorList[i])
        return plotList

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


#------------------------ External Functions ---------------------------------------------

def openSaveFile(filename=''):
    if filename == '':
        file = open(fd.askopenfilename(filetypes=[('Excel-o-meter Save File','*.esf')]), 'rb')
    else:
        file = open(filename, 'rb')

    sensorDataObject = pickle.Unpickler(file).load()
    file.close()
    return(sensorDataObject)

def saveFile(sensorDataObject, filename=''):
    if filename == '':
        sfFileName = fd.asksaveasfilename(filetypes=[("Excelometer Save Files", "*.esf" ),("All files", "*")], defaultextension='.esf')
        file = open(sfFileName, 'wb')
        sensorDataObject.runData['runTitle'] = sfFileName.split('.')[0].split('/')[-1]
    else:
        sfFileName = filename + '.esf'
        file = open(sfFileName, 'wb')

    sensorDataObject.saved = [True, True]
    pickle.Pickler(file).dump(sensorDataObject)
    file.close()
    return
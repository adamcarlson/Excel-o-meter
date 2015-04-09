__author__ = 'Adam Carlson'


import tkinter.filedialog as fd
import numpy as np
from subprocess import Popen, PIPE
import matplotlib.pyplot as plt
import os

X, Y, Z = 0, 1, 2

class SensorData(object):
    def __init__(self, numberOfSensors = 3, Hz=800):
        self.interval = 1/Hz
        self.numberOfSensors = numberOfSensors

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

    def runUnpacker(self, filename):
        process = Popen([r"eom.exe", "{}".format(filename)], stdout=PIPE)
        stderr, stdout = process.communicate()
        process.wait()
        return int.from_bytes(stdout, byteorder='little') # may need to be 'big'

    def newData(self, sensorDataObject):
        self.data = sensorDataObject.data
        self.interval = sensorDataObject.interval
        self.numberOfSensors = sensorDataObject.numberOfSensors
        self.intervalCount = sensorDataObject.intervalCount
        self.plotList = sensorDataObject.plotList

    def generatePlots(self, sensorList):
        plotList = [plt.figure(figsize=(1,1), dpi=100, frameon=False) for i in range(3)]
        for i, item in enumerate(plotList):
            plot = plotList[i].add_subplot(111)
            plot.set_xlabel(r'$samples$')
            plot.set_title('Acceleration')
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
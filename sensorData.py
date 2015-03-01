__author__ = 'Adam Carlson'

import classes
import tkinter.filedialog as fd
import tkinter as tk
import numpy as np
from numpy import sin, pi
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.animation as anm
import os

X, Y, Z = 0, 1, 2

class SensorData(object):
    def __init__(self, Hz):
        self.intervals = 1/Hz

    def importData(self):
        self.filename = fd.askopenfilename()
        if self.filename.split('.')[-1] == 'sac':
            classes.importer(self.filename)
            record_dtype = np.dtype([('x_data', np.float32), ('y_data', np.float32), ('z_data', np.float32)])
            self.s1Data = np.fromfile('s1.dat', dtype=record_dtype)
            #self.s2Data = np.fromfile('s2.dat', dtype=record_dtype)
            #self.s3Data = np.fromfile('s3.dat', dtype=record_dtype)

            for i in range(1):
                os.remove('s{}.dat'.format(i+1))

            self.s1DList = [self.s1Data['x_data'], self.s1Data['y_data'], self.s1Data['z_data']]
            #self.s2DList = [self.s2Data['x_data'], self.s2Data['y_data'], self.s2Data['z_data']]
            #self.s3DList = [self.s3Data['x_data'], self.s3Data['y_data'], self.s3Data['z_data']]

            self.truncateToShortest()
            self.t = np.arange(0.0,(self.smallestSize()*self.intervals),self.intervals)

            self.s1DPlotList = self.generatePlots(self.s1DList)
            #self.s2DPlotList = self.generatePlots(self.s2DList)
            #self.s3DPlotList = self.generatePlots(self.s3DList)
            self.SmallPlotList = [self.s1DPlotList, self.s1DPlotList, self.s1DPlotList]

    def newData(self, newSD):
        self.s1DList = newSD.s1DList
        #self.s2DList = newSD.s2DList
        #self.s3DList = newSD.s3DList

        self.s1DPlotList = newSD.s1DPlotList
        #self.s2DPlotList = newSD.s2DPlotList
        #self.s3DPlotList = newSD.s3DPlotList

        self.SmallPlotList = newSD.SmallPlotList


    def generatePlots(self, sensorList):
        s = sin(2*pi*self.t)
        plotList = [plt.figure(figsize=(1,1), dpi=100, frameon=False) for i in range(6)]
        for i in range(6):
            plot = plotList[i].add_subplot(111)
            plot.set_xlabel(r'$samples$')
            if i % 2 == 0:
                plot.set_title('Acceleration')
                plot.set_ylabel(r'$m/s^2$')
            else:
                plot.set_title('Velocity')
                plot.set_ylabel(r'$m/s$')
            if( i == 0):
                plot.plot(self.t, sensorList[X])
            elif( i == 2):
                plot.plot(self.t, sensorList[Y])
            elif( i == 4):
                plot.plot(self.t, sensorList[Z])
            else:
                plot.plot(self.t,s)

        return plotList

    def draw4DGraph(self, graphFrame, sensorNum, sensorList):
        figure = plt.figure(figsize=(1,1), dpi=100, frameon=False)
        canvas = classes.ActuallyWorkingFigureCanvas(figure, graphFrame)
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        plot = Axes3D(figure)
        line = plot.plot([sensorList[X][0], sensorList[X][1]],
                         [sensorList[Y][0], sensorList[Y][1]],
                         [sensorList[Z][0], sensorList[Z][1]])[0]

        plot.set_xlim3d([0.0, 5.0])
        plot.set_xlabel('X')
        plot.set_ylim3d([0.0, 5.0])
        plot.set_ylabel('Y')
        plot.set_zlim3d([0.0, 5.0])
        plot.set_zlabel('Z')
        plot.set_title('Sensor {}'.format(sensorNum))

        anm.FuncAnimation(figure, self.update_lines, np.size(sensorList[X]), fargs=(sensorList, line), interval=1, blit=False)
        toolbar = classes.ActuallyWorkingToolbar(canvas, graphFrame)
        canvas.show()
        toolbar.update()
        toolbar.pack(side='top', fill='both')

        return figure

    def update_lines(self, num, data, line):
        if num > 20:
            x = num - 20
        else:
            x = 0
        line.set_data([data[0][i] for i in range(x, num)], [ data[1][i] for i in range(x, num)])
        line.set_3d_properties([data[2][i] for i in range(x, num)])
        return line

    # Utility Methods
    def truncateToShortest(self):
        count = self.smallestSize()
        for i in range(3):
            self.s1DList[i] = self.s1DList[i][0:count]
            #self.s2DList[i] = self.s2DList[i][0:count]
            #self.s3DList[i] = self.s3DList[i][0:count]

    def smallestSize(self):
        count = 0
        for item in self.s1DList:
            size = np.size(item)
            if count == 0 or size < count:
                count = size
        '''
        for item in self.s2DList:
            size = np.size(item)
            if count == 0 or size < count:
                count = size

        for item in self.s3DList:
            size = np.size(item)
            if count == 0 or size < count:
                count = size
        '''
        return count

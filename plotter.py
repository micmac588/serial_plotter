#!/usr/bin/env python3
import numpy as np
import itertools
import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
import matplotlib.animation as animation

class Plotter():
    DELTA = 10 # y axis percentage over and under the last temperature

    def __init__(self, serial_reader, measure, logger):
        self.fig, self.ax = plt.subplots()
        self.line, = self.ax.plot([], [], lw=2)
        self.ax.grid()
        self.ydata = []
        self.xdata = []
        self.serial_reader = serial_reader
        self.measure = measure
        self.count = 0
        self.logger = logger

    def start(self):
        ani = animation.FuncAnimation(self.fig, self.run, self.data_gen, interval=100, init_func=self.init)
        plt.show()

    def get_measure_to_plot(self):
        if self.measure == "temperature":
            return self.serial_reader.get_temperature()
        if self.measure == "pressure":
            return self.serial_reader.get_pressure()

    def set_ylim(self):
        y = self.get_measure_to_plot()
        ymin = y - y * self.DELTA/100
        ymax = y + y * self.DELTA/100
        self.ax.set_ylim(ymin, ymax)

    def init(self):

        self.set_ylim()

        self.ax.set_xlim(0, 5)
        del self.xdata[:]
        del self.ydata[:]
        self.line.set_data(self.xdata, self.ydata)
        return self.line,

    def data_gen(self):
        for cnt in itertools.count():
            yield self.serial_reader.get_count(), self.get_measure_to_plot()

    def run(self, data):
        # update the data
        t, y = data
        self.xdata.append(t)
        self.ydata.append(y)

        xmin, xmax = self.ax.get_xlim()
        if t >= xmax:
            self.ax.set_xlim(xmin, 2*xmax)
            self.ax.figure.canvas.draw()

        ymin, ymax = self.ax.get_ylim()
        if y >= ymax or y <= ymin:
            self.set_ylim()
            self.ax.figure.canvas.draw()

        self.line.set_data(self.xdata, self.ydata)

        return self.line,
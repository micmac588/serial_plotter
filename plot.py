import serial
from threading import Thread, Event
from datetime import datetime
import numpy as np
import itertools
import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import logging


SERIAL_PORT = "/dev/ttyACM0"
SERIAL_BAUD_RATE = 9600
LOGGER_LEVEL = logging.DEBUG
DELTA = 10 # y axis percentage over and under the last temperature

pressure = 0
temperature = 0
count = 0

class MonThread (Thread):
    def __init__(self, started_evt, logger):
        Thread.__init__(self)
        self.started_evt = started_evt
        self.logger = logger
        self.ser = serial.Serial(port=SERIAL_PORT,
                                 baudrate=SERIAL_BAUD_RATE,
                                 parity=serial.PARITY_NONE,
                                 stopbits=serial.STOPBITS_ONE,
                                 bytesize=serial.EIGHTBITS,
                                 timeout=1)
        self.ser.close()
        self.ser.open()
        if self.ser.isOpen():
            logger.debug(self.ser.name + " is open…")
            logger.debug(self.ser.get_settings())

    def run(self):
        global pressure
        global temperature
        global count

        self.logger.info("Starts to get temperature and pressure at %s" % datetime.now())

        while(1):
            try:
                # line are 'temperature:pressure\n'
                line = self.ser.readline().decode().split('\n')[0]
                if line:
                    self.logger.debug(line)
                    temperature = float(line.split(':')[0])
                    pressure = float(line.split(':')[1])
                    count = count + 1
                    started_evt.set()

            except Exception as e:
                self.logger.warning("Exception: %s" % e)
                continue

def set_y_lim(y):
    ymin = y - y*DELTA/100
    ymax = y + y*DELTA/100
    ax.set_ylim(ymin, ymax)

def init():
    global pressure
    global temperature
    global count

    set_y_lim(temperature)

    ax.set_xlim(0, 5)
    del xdata[:]
    del ydata[:]
    line.set_data(xdata, ydata)
    return line,

def data_gen():
    global count
    global pressure
    global temperature

    for cnt in itertools.count():
        yield count, temperature

def run(data):
    # update the data
    t, y = data
    xdata.append(t)
    ydata.append(y)


    xmin, xmax = ax.get_xlim()
    if t >= xmax:
        ax.set_xlim(xmin, 2*xmax)
        ax.figure.canvas.draw()

    ymin, ymax = ax.get_ylim()
    if y >= ymax or y <= ymin:
        set_y_lim(y)
        ax.figure.canvas.draw()

    line.set_data(xdata, ydata)

    return line,


logger = logging
logger.basicConfig(level=LOGGER_LEVEL)
# Create the event object that will be used to signal startup
started_evt = Event()
ydata = []
xdata = []
m = MonThread(started_evt, logger)
m.daemon = True
m.start()

fig, ax = plt.subplots()
line, = ax.plot([], [], lw=2)
ax.grid()

# Wait for the first measure to be received
started_evt.wait()

ani = animation.FuncAnimation(fig, run, data_gen, interval=100, init_func=init)
plt.show()

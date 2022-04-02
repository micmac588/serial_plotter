from re import I
import serial
import queue
import threading
import time
import numpy as np
from plotter import Plotter
from plotter import PlotterType
import logging

MAX_NUM_OF_MEASURES = 1000


class MonThread (threading.Thread):
    def __init__(self, my_list, lock, logger):
        threading.Thread.__init__(self)
        self.pressures = my_list
        self.lock = lock
        self.ser = serial.Serial(port="COM4", baudrate=9600, timeout=1)
        self.ser.close()
        self.ser.open()
        if self.ser.isOpen():
            logger.debug(self.ser.name + " is open…")
            logger.debug(self.ser.get_settings())

    def run(self):
        while(1):
            pressure = self.ser.readline()
            try:
                logger.debug("Got a pressure %f" % float(pressure))
                current_len = len(self.pressures)
                if current_len < MAX_NUM_OF_MEASURES:
                    self.pressures.insert(0, float(pressure))
                else:
                    for index in range(current_len-1, 0, -1):
                        self.pressures[index] = self.pressures[index-1]
                    self.pressures[0] = float(pressure)
                try:
                    self.lock.release()
                except RuntimeError as e:
                    logger.warning(e)
                logger.debug(self.pressures)
            except ValueError:
                continue


def build_to_plot(pressures, i, logger):
    current_len = len(pressures)
    x = np.linspace(0, current_len-1, current_len)
    to_plot = [
        {
            "title": "Pressure",
            "type": PlotterType.PLOT,
            "data": [x, pressures],
        },
    ]
    return to_plot


logger = logging
logger.basicConfig(level=logging.INFO)
threadLock = threading.Lock()
pressures = []
m = MonThread(pressures, threadLock, logger)
m.daemon = True
m.start()
i = 0
pl = Plotter([
    {
        "type": PlotterType.PLOT,
    }
])

while threadLock.acquire(blocking=True):
    try:
        pl.set_to_plot(build_to_plot(pressures, i*5, logger))
        pl.show(blocking=False)
    except Exception as e:
        logger.critical(e)
        break
    i = i + 1
exit(-1)

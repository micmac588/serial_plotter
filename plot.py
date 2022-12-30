import serial
import threading
from datetime import datetime
import numpy as np
from plotter import Plotter
from plotter import PlotterType
import logging


SERIAL_PORT = "/dev/ttyACM0"
SERIAL_BAUD_RATE = 9600
LOGGER_LEVEL = logging.INFO


class MonThread (threading.Thread):
    def __init__(self, pressures, temperatures, lock, logger):
        threading.Thread.__init__(self)
        self.pressures = pressures
        self.temperatures = temperatures
        self.lock = lock
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

        self.logger.info("Starts to get temperature and pressure at %s" % datetime.now())

        while(1):
            # line are 'temperature:pressure\n'
            line = self.ser.readline().decode().split('\n')[0]
            if line:
                self.logger.debug(line)
                try:
                    self.temperatures.append(float(line.split(':')[0]))
                    self.pressures.append(float(line.split(':')[1]))
                    try:
                        self.lock.release()
                    except RuntimeError as e:
                        self.logger.warning("Exception RuntimeError: %s" % e)
                        continue

                except ValueError as e:
                    self.logger.warning("Exception ValueError %s: %s" % (line, e))
                    continue


def build_to_plot(pressures, temperatures):
    current_len = len(temperatures)
    x = np.linspace(0, max(10,current_len-1), current_len)
    to_plot = [
        {
            "title": "Temperature",
            "type": PlotterType.PLOT,
            "data": [x, temperatures]
        },
        {
            "title": "Pressure",
            "type": PlotterType.PLOT,
            "data": [x, pressures]
        }
    ]
    return to_plot


logger = logging
logger.basicConfig(level=LOGGER_LEVEL)
threadLock = threading.Lock()
threadLock.acquire()  # locked by default
pressures = []
temperatures = []
m = MonThread(pressures, temperatures, threadLock, logger)
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
        pl.set_to_plot(build_to_plot(pressures, temperatures))
        pl.show(blocking=False)
    except Exception as e:
        logger.critical(e)
        break
    i = i + 1
exit(-1)

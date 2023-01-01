import serial
from threading import Thread, Event
from datetime import datetime

SERIAL_PORT = "/dev/ttyACM0"
SERIAL_BAUD_RATE = 9600

class SerialReader (Thread):
    def __init__(self, evt, logger):
        Thread.__init__(self)
        Thread.daemon = True
        self.evt = evt
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
            self.logger.debug(self.ser.name + " is open…")
            self.logger.debug(self.ser.get_settings())

        self.temperature = 0
        self.pressure = 0
        self.count = 0

    def run(self):

        self.logger.info("Starts to get temperature and pressure at %s" % datetime.now())

        while(1):
            try:
                # line are 'temperature:pressure\n'
                line = self.ser.readline().decode().split('\n')[0]
                if line:
                    self.temperature = float(line.split(':')[0])
                    self.pressure = float(line.split(':')[1])
                    self.count = self.count + 1
                    self.logger.debug("%s:%s:%s" %(self.count, self.temperature, self.pressure))
                    self.evt.set()

            except Exception as e:
                self.logger.warning("Exception: %s" % e)
                continue

    def get_pressure(self):
        return self.pressure

    def get_temperature(self):
        return self.temperature

    def get_count(self):
        return self.count


    
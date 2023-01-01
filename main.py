#!/usr/bin/env python3
import argparse
import logging
from plotter import Plotter
from serial_reader import SerialReader
from threading import Event


def prepare_logger(logger_name, verbosity, log_file=None):
    """Initialize and set the logger.

    :param logger_name: the name of the logger to create
    :type logger_name: string
    :param verbosity: verbosity level: 0 -> default, 1 -> info, 2 -> debug
    :type  verbosity: int
    :param log_file: if not None, file where to save the logs.
    :type  log_file: string (path)
    :return: a configured logger
    :rtype: logging.Logger
    """

    logger = logging.getLogger(logger_name)

    log_level = logging.WARNING - (verbosity * 10)
    log_format = "[%(filename)-30s:%(lineno)-4d][%(levelname)-7s] %(message)s"
    logging.basicConfig(format=log_format, level=log_level)

    # create and add file logger
    if log_file:
        formatter = logging.Formatter(log_format)
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    return logger


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--measure", help="what to plot [temperature|pressure].", required=False, default="pressure")
    parser.add_argument("-v", "--verbosity", action="count", default=0, help="increase the verbosity", required=False)
    parser.add_argument("-l", "--logfile", help="log file name", required=False)

    args = parser.parse_args()

    logger = prepare_logger("serial_plotter", args.verbosity, args.logfile)

    # Create the event object that will be used to signal startup
    started_evt = Event()

    sr = SerialReader(started_evt, logger)
    sr.start()

    pl = Plotter(sr,args.measure, logger)

    # Wait for the first measure to be received
    started_evt.wait()

    pl.start()


if __name__ == "__main__":
    main()

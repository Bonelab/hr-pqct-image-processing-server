"""
ip_logging.py
Author: Ian Smith
Description: Logging class for the image processing server
Note: Will probably change the implementation of logging in the future
"""
import logging
import constants


class Logger:
    def __init__(self):
        """
        Constructor Method
        """
        self.debug_logger = self._create_logger("debug", constants.DEBUG, logging.DEBUG)
        self.error_logger = self._create_logger("error", constants.ERROR, logging.ERROR)

    def _create_logger(self, name, filename, level):
        """
        Create a logger for a specific purpose
        :param name: Name of the logger you want to create
        :param filename: Filename/Location for the log file of this logger
        :param level: Logging level (i.e. debug, warning, error...)
        :return: Returns the custom created logger
        """
        logger = logging.getLogger("{}-{}-{}".format(self.__class__.__name__, id(self), name))
        logger.setLevel(level)
        if not logger.handlers:
            handler = logging.FileHandler(filename)
            handler.setLevel(level)
            form = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(form)
            logger.addHandler(handler)
            logger.propagate = False
        return logger

    def log_error(self, error_msg):
        """
        Call this method to log an error (Use for exceptions)
        :param error_msg: Message you want the logs to display
        :return: None
        """
        self.error_logger.error(error_msg)

    def log_debug(self, debug_msg):
        """
        Call this method to log lower level activities that should be logged (Enqueueing, Dequeueing, Processing, Sending ...)
        :param debug_msg: Message you want the logs to display
        :return: None
        """
        self.debug_logger.debug(debug_msg)
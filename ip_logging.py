import logging

DEBUG = "debug.log"  # Change to logs/debug.log
ERROR = "error.log"  # Change to logs/error.log

class Logger:
    def __init__(self):
        self.debug_logger = self._create_logger("debug", DEBUG, logging.DEBUG)
        self.error_logger = self._create_logger("error", ERROR, logging.ERROR)


    def _create_logger(self, name, filename, level):
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
        self.error_logger.error(error_msg)

    def log_debug(self, debug_msg):
        self.debug_logger.debug(debug_msg)
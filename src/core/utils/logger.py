import logging

from core.constants import App


class Logger:
    def __init__(self, name):
        # Configure the logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)

        # clear handlers to avoid duplicate logs
        if self.logger.hasHandlers():
            self.logger.handlers.clear()

        # Create a console handler and set the log level
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        # create a file handler and set the log level
        file_handler = logging.FileHandler(f"{App.NAME.value}.log")
        file_handler.setLevel(logging.DEBUG)

        # Create a formatter that includes the timestamp with milliseconds
        formatter = logging.Formatter('[%(asctime)s.%(msecs)03d] [%(levelname)s] [%(name)s]: %(message)s',
                                      datefmt='%Y-%m-%d %H:%M:%S')

        # Set the formatter for handlers
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)

        # Add the handlers to the logger
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)

    def get_logger(self):
        return self.logger

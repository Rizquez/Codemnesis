# MODULES (EXTERNAL)
# ---------------------------------------------------------------------------------------------------------------------
from __future__ import annotations

import os
import logging
from logging.handlers import RotatingFileHandler
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from logging import Logger
# ---------------------------------------------------------------------------------------------------------------------

# MODULES (INTERNAL)
# ---------------------------------------------------------------------------------------------------------------------
from common.constants import ALGORITHM
# ---------------------------------------------------------------------------------------------------------------------

# OPERATIONS / CLASS CREATION / GENERAL FUNCTIONS
# ---------------------------------------------------------------------------------------------------------------------

FILE = 'Trace-Report.log'

class HandlerLogger:
    """
    Class responsible for managing the configuration of the logger used in the application.

    Its purpose is to ensure that each component of the application has a consistent and separate logging system.

    **Key points:**
        - **Different levels:**
            - Algorithm → supports `DEBUG`, `INFO`, `WARNING`, `ERROR`.
    """

    @classmethod
    def set(cls, output: str) -> None:
        """
        Configures the logger associated with the **Algorithm** layer.

        Args:
            output (str):
                Path of the directory where the file will be stored.
        """
        logger = logging.getLogger(ALGORITHM)
        if logger.handlers: 
            return

        logger.setLevel(logging.DEBUG)

        # Prevents messages from being sent to the root logger 
        # so that they are not duplicated in other handlers
        logger.propagate = False
        
        logger.addHandler(cls.__handler(file=os.path.join(output, FILE)))
        logger.addHandler(cls.__stream_handler())
        
    @staticmethod
    def close(logger: Logger) -> None:
        """
        Closes and removes all handlers associated with a specific logger.

        - Iterates through all active handlers of the logger.
        - Closes each handler to free file descriptors.
        - Removes the handlers from the logger to leave it clean.

        Args:
            logger (Logger):
                Instance of the logger to be closed.
        """
        lst_handlers = logger.handlers[:]
        for handler in lst_handlers:
            handler.close()
            logger.removeHandler(handler)

    @staticmethod
    def __handler(
        file: str, 
        *, 
        level: int = logging.INFO, 
        size: int = 1024 * 1024 * 5,
        backup: int = 10,
        encoding: str = 'utf-8'
    ) -> RotatingFileHandler:
        """
        Create a `RotatingFileHandler` to write logs to a file with automatic rotation.

        Args:
            file (str):
                Full path of the log file.
            level (int):
                Log level.
            size (int):
                Maximum size the file can have before backing up.
            backup (int):
                Number of backups that can be generated.
            encoding (str):
                Encoding format for writing the log file.

        Returns:
            RotatingFileHandler:
                Handler configured with format and rotation.
        """
        handler = RotatingFileHandler(
            file, 
            maxBytes=size, 
            backupCount=backup, 
            encoding=encoding,
            delay=True # It does not open the file until the first message is written
        )

        handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
        handler.setLevel(level)

        return handler
    
    @staticmethod
    def __stream_handler() -> logging.StreamHandler:
        """
        Creates a `StreamHandler` to display logs directly on the console.

        Returns:
            StreamHandler:
                Handler configured for standard output.
        """
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
        handler.setLevel(logging.DEBUG)

        return handler

# ---------------------------------------------------------------------------------------------------------------------
# END OF FILE
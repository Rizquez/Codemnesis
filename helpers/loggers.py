# MODULES (EXTERNAL)
# ---------------------------------------------------------------------------------------------------------------------
import os
import logging
from typing import TYPE_CHECKING
from logging.handlers import RotatingFileHandler

if TYPE_CHECKING:
    from logging import Logger
# ---------------------------------------------------------------------------------------------------------------------

# MODULES (INTERNAL)
# ---------------------------------------------------------------------------------------------------------------------
from settings.constants import ALGORITHM

if TYPE_CHECKING:
    from settings.algorithm import Settings
# ---------------------------------------------------------------------------------------------------------------------

# OPERATIONS / CLASS CREATION / GENERAL FUNCTIONS
# ---------------------------------------------------------------------------------------------------------------------

LOGGER_FILE = 'AutoDocMind'

class ManageLogger:
    """
    Class responsible for managing the configuration of the logger used in the application.

    This class centralizes the initialization and configuration of the logger for the `Algorithm` layer. 

    Its purpose is to ensure that each component of the application has a consistent and separate logging system.

    **Key points:**
        - **Different levels:**
            - Algorithm → supports `DEBUG`, `INFO`, `WARNING`, `ERROR`.
    """

    @classmethod
    def algorithm(cls, settings: 'Settings') -> None:
        """
        Configures the logger associated with the **Algorithm** layer.

        **Notes:**
            - This method *creates the output directory* that will contain all generated files.

        Args:
            settings (Settings):
                Object containing the general settings for executing the algorithm.
        """
        folder = settings.output
        
        os.makedirs(folder, exist_ok=True)

        file = os.path.join(folder, f'{LOGGER_FILE}.log')

        logger = logging.getLogger(ALGORITHM)
        if logger.handlers: 
            return # Avoid duplicating handlers if they have already been configured
        
        # The file only saves INFO/ERROR/WARNING, even if the logger accepts DEBUG
        logger.setLevel(logging.DEBUG)
        logger.propagate = False
        logger.addHandler(cls.__handler(file))
        logger.addHandler(cls.__stream_handler())
        
    @staticmethod
    def close_logger(logger: 'Logger') -> None:
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
            level (int, optional):
                Log level.
            size (int, optional):
                Maximum size the file can have before backing up.
            backup (int, optional):
                Number of backups that can be generated.
            encoding (str, optional):
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
            delay=True # The file is created only when the first log is written
        )

        handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
        handler.setLevel(level)

        return handler
    
    @staticmethod
    def __stream_handler() -> logging.StreamHandler:
        """
        Creates a `StreamHandler` to display logs directly on the console.

        Returns:
            logging.StreamHandler:
                Handler configured for standard output.
        """
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
        handler.setLevel(logging.DEBUG) # Console will display DEBUG (more detailed than the file)

        return handler

# ---------------------------------------------------------------------------------------------------------------------
# END OF FILE
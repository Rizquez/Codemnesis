# MODULES (EXTERNAL)
# ---------------------------------------------------------------------------------------------------------------------
import time
import psutil
import logging
# ---------------------------------------------------------------------------------------------------------------------

# MODULES (INTERNAL)
# ---------------------------------------------------------------------------------------------------------------------
from src.execute import execute
from handlers.console import Console
from settings.algorithm import Settings
from helpers.loggers import ManageLogger
from settings.constants import ALGORITHM, ALGORITHM_VERSION
# ---------------------------------------------------------------------------------------------------------------------

# OPERATIONS / CLASS CREATION / GENERAL FUNCTIONS
# ---------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    start = time.time()

    before = psutil.virtual_memory().used

    settings = Settings(Console.arguments())

    ManageLogger.algorithm(settings)

    logger = logging.getLogger(ALGORITHM)

    logger.info("Execution summary")
    logger.info(f"Algorithm version: {ALGORITHM_VERSION}")

    execute(settings)

    end = time.time()

    after = psutil.virtual_memory().used

    logger.info(f"Total execution time: {round(end - start, 3)} seconds")

    logger.info(f"Total memory consumed: {round((after - before) / pow(1024, 2), 2)} megabytes")

    ManageLogger.close_logger(logger)

# ---------------------------------------------------------------------------------------------------------------------
# END OF FILE
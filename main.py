# MODULES (EXTERNAL)
# ---------------------------------------------------------------------------------------------------------------------
import time, psutil, logging
# ---------------------------------------------------------------------------------------------------------------------

# MODULES (INTERNAL)
# ---------------------------------------------------------------------------------------------------------------------
from src.execute import execute
from common.settings import Settings
from handlers.arguments import Arguments
from handlers.logger import HandlersLogger
from common.constants import ALGORITHM, ALGORITHM_VERSION
# ---------------------------------------------------------------------------------------------------------------------

# OPERATIONS / CLASS CREATION / GENERAL FUNCTIONS
# ---------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    start = time.time()

    before = psutil.virtual_memory().used

    settings = Settings(Arguments.get())

    HandlersLogger.set(settings.output)

    logger = logging.getLogger(ALGORITHM)

    logger.info("Execution summary")
    logger.info(f"Algorithm version: {ALGORITHM_VERSION}")

    execute(settings)

    end = time.time()

    after = psutil.virtual_memory().used

    logger.info(f"Total execution time: {round(end - start, 3)} seconds")
    
    logger.info(f"Total memory consumed: {round((after - before) / pow(1024, 2), 2)} megabytes")

    HandlersLogger.close(logger)

# ---------------------------------------------------------------------------------------------------------------------
# END OF FILE
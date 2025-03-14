import logging
from config import LOG_FILE

# Configure logging
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

def get_logger():
    logger = logging.getLogger("hospital_scraper")
    logger.setLevel(logging.INFO)

    # Create a file handler to log messages to a file
    file_handler = logging.FileHandler("scraper.log")
    file_handler.setLevel(logging.INFO)

    # Create a stream handler to log messages to the terminal
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)

    # Define a common format for both handlers
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)
    stream_handler.setFormatter(formatter)

    # Add handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    return logger

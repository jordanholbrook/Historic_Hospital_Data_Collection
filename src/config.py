import os

# API Configuration
SCRAPFLY_URL = "https://api.scrapfly.io/scrape"

# Base URL
BASE_URL = "https://www.asylumprojects.org"

# Output Directory
OUTPUT_DIR = "./output/"

# Log Directory
LOG_DIR = "./logs/"
LOG_FILE = os.path.join(LOG_DIR, "scraper.log")

# Retry configuration for fetching hospital details
MAX_RETRIES = 3
RETRY_DELAY = 10

# Ensure directories exist
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

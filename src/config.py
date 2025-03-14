import os

# API Configuration
SCRAPFLY_URL = "https://api.scrapfly.io/scrape"
API_KEY = "your_api_key_here"

# Base URL
BASE_URL = "https://www.asylumprojects.org"

# Output Directory
OUTPUT_DIR = "./output/"

# Log Directory
LOG_DIR = "./logs/"
LOG_FILE = os.path.join(LOG_DIR, "scraper.log")

# Ensure directories exist
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

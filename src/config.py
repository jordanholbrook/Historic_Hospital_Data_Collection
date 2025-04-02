import os

# OpenAI API Configuration
#API_KEY = os.getenv("OPENAI_API_KEY")  # Set your API key as an environment variable

URL = "https://api.openai.com/v1/chat/completions"
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}
MODEL = "gpt-4o"

# Directories
RAW_DIR = "/Users/jordanholbrook/Repos/Historic_Hospital_Data_Collection/output/saved_data/test_LLM_pipeline_1"
TEMP_DIR = "/Users/jordanholbrook/Repos/Historic_Hospital_Data_Collection/output/processed_data_test1"
LINKS_FILE = "/Users/jordanholbrook/Repos/Historic_Hospital_Data_Collection/output/hospital_links.csv"
FINAL_OUTPUT = f"{TEMP_DIR}/processed_hospitals_combined.csv"

# API Configuration
SCRAPFLY_URL = "https://api.scrapfly.io/scrape"
#API_KEY = "your_api_key_here"

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

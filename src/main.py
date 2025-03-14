import time
import argparse
from scraper import get_state_links, get_hospital_links, get_hospital_details
from data_handler import save_to_csv
from logger import get_logger
from config import MAX_RETRIES, RETRY_DELAY

logger = get_logger()

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Scrape hospital data.")
    parser.add_argument(
        "--state", 
        type=str, 
        help="Specify a state to scrape data for (e.g., 'California'). If not provided, all states will be scraped."
    )
    args = parser.parse_args()

    # Get state links
    state_links = get_state_links()

    # Filter for a specific state if provided
    if args.state:
        state_links = state_links[state_links["State"] == args.state]
        if state_links.empty:
            logger.error(f"No data found for the specified state: {args.state}")
            return

    hospital_links = []
    for _, state_url in state_links.itertuples(index=False):
        logger.info(f"Scraping hospitals for state: {state_url}")
        df_hospitals = get_hospital_links(state_url)
        hospital_links.extend(df_hospitals["Hospital Link"].dropna().tolist())
        time.sleep(3)
    
    hospital_details = []
    for hospital_url in hospital_links:
        details = get_hospital_details(hospital_url, MAX_RETRIES, RETRY_DELAY)
        hospital_details.append(details)
        time.sleep(5)
    
    save_to_csv(hospital_details, "hospital_details.csv")
    logger.info("Scraping completed and data saved!")

if __name__ == "__main__":
    main()

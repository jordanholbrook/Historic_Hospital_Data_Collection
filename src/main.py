import time
import argparse
import pandas as pd
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

    # Process each state individually
    for _, state_url in state_links.itertuples(index=False):
        logger.info(f"Scraping hospitals for state: {state_url}")
        df_hospitals = get_hospital_links(state_url)
        state_name = df_hospitals["State"].iloc[0]  # Extract the state name from the DataFrame

        hospital_links = df_hospitals["Hospital Link"].dropna().tolist()
        hospital_details = []

        # Process each hospital in the state
        for hospital_url in hospital_links:
            details = get_hospital_details(hospital_url, state_name, MAX_RETRIES, RETRY_DELAY)
            hospital_details.append(details)
            time.sleep(5)

        # Save the hospital details for the current state to a CSV file
        output_filename = f"hospital_details_{state_name}.csv"
        save_to_csv(hospital_details, output_filename)
        logger.info(f"Scraping completed for {state_name}. Data saved to {output_filename}.")

        # Pause before moving to the next state
        time.sleep(3)

    logger.info("All states processed!")

if __name__ == "__main__":
    main()

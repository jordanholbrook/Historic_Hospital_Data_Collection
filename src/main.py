import time
from scraper import get_state_links, get_hospital_links, get_hospital_details
from data_handler import save_to_csv
from logger import get_logger

logger = get_logger()

def main():
    state_links = get_state_links()
    
    hospital_links = []
    for _, state_url in state_links.itertuples(index=False):
        logger.info(f"Scraping hospitals for state: {state_url}")
        df_hospitals = get_hospital_links(state_url)
        hospital_links.extend(df_hospitals["Hospital Link"].dropna().tolist())
        time.sleep(3)
    
    hospital_details = []
    for hospital_url in hospital_links:
        details = get_hospital_details(hospital_url)
        hospital_details.append(details)
        time.sleep(5)
    
    save_to_csv(hospital_details, "hospital_details.csv")
    logger.info("Scraping completed and data saved!")

if __name__ == "__main__":
    main()

import os
import glob
import logging
import pandas as pd
from config import RAW_DIR, TEMP_DIR, LINKS_FILE, FINAL_OUTPUT
from data_handler import extract_llm_data, clean_hospital_df, process_hospital_data

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def run_pipeline():
    logging.info("Starting pipeline...")

    # Step 1: Run LLM extraction
    logging.info("Extracting data using LLM...")
    extract_llm_data(RAW_DIR, TEMP_DIR)

    # Step 2: Load processed CSVs (LLM outputs)
    logging.info("Loading processed CSV files...")
    input_files = glob.glob(os.path.join(TEMP_DIR, "processed_*.csv"))

    all_dfs = []
    for file_path in input_files:
        try:
            df = pd.read_csv(file_path)
            all_dfs.append(df)
        except Exception as e:
            state_code = os.path.basename(file_path).replace('.csv', '')
            logging.error(f"Could not read file for state: {state_code}. Reason: {e}")

    if not all_dfs:
        logging.critical("No CSV files could be successfully read from the directory.")
        raise ValueError("❌ No CSV files could be successfully read from the directory.")

    df_all = pd.concat(all_dfs, ignore_index=True)

    # Step 3: Load hospital links and merge in Hospital_Type
    logging.info("Merging hospital links...")
    hospital_links = pd.read_csv(LINKS_FILE, names=["State", "Hospital_Type", "Hospital_Name", "URL"], header=None)
    df_all = df_all.merge(hospital_links[['URL', 'Hospital_Type']].drop_duplicates(), on='URL', how='left')

    # Step 4: Clean and process
    logging.info("Cleaning and processing data...")
    df_cleaned = clean_hospital_df(df_all)
    df_processed = process_hospital_data(df_cleaned)

    # Step 5: Save final output
    logging.info(f"Saving final output to {FINAL_OUTPUT}...")
    df_processed.to_csv(FINAL_OUTPUT, index=False)
    logging.info("Pipeline completed successfully!")

if __name__ == "__main__":
    run_pipeline()

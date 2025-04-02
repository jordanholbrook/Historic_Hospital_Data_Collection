import os
import time
import pandas as pd
import numpy as np
from pathlib import Path
from config import OUTPUT_DIR
from api_handler import call_openai_api, build_prompt

def save_to_csv(data: list, filename: str):
    """Appends data to CSV file."""
    df = pd.DataFrame(data)
    df.to_csv(f"{OUTPUT_DIR}{filename}", index=False, header=True) 
    #df.to_csv(f"{OUTPUT_DIR}{filename}", index=False, mode='a', header=False)



# ---------------------------
# 🧼 Data Cleaning
# ---------------------------
def clean_hospital_df(df):
    def to_4digit_int(val):
        try:
            return int(str(val).strip()[:4])
        except:
            return pd.NA

    def clean_population(val):
        try:
            return int(str(val).strip().split()[0].replace(',', ''))
        except:
            return pd.NA

    def contains_kirkbride(row):
        fields = [str(row.get('Building Style', '')), str(row.get('Architecture Style', '')), str(row.get('Raw Text', ''))]
        return int(any('kirkbride' in field.lower() for field in fields))

    def clean_hospital_type(val):
        return str(val).replace("[edit]", "").strip().title() if pd.notna(val) else pd.NA

    def split_alt_names(val):
        return [part.strip() for part in str(val).strip(' |').split('|') if part.strip()] if pd.notna(val) else []

    # Apply cleaning
    for col in ['Established', 'Construction Began', 'Opened', 'Closed', 'year_opened_LLM', 'year_closed_LLM']:
        df[col] = df[col].apply(to_4digit_int).astype('Int64')

    for col in ['Peak Patient Population', 'number_of_beds_LLM', 'number_of_patients_LLM', 'peak_patient_population_LLM']:
        df[col] = df[col].apply(clean_population).astype('Int64')

    df['kirkbride_flag'] = df.apply(contains_kirkbride, axis=1)
    df['incomplete_page_flag'] = df['URL'].str.contains('redlink', case=False, na=False).astype(int)
    df['City'] = df['Location'].str.split(',', n=1).str[0].str.strip()
    df['Hospital_Type'] = df['Hospital_Type'].apply(clean_hospital_type)

    alt_names_expanded = df['Alternate Names'].apply(split_alt_names).apply(pd.Series)
    alt_names_expanded.columns = [f'alt_name{i+1}' for i in alt_names_expanded.columns]
    for i in range(1, 6):
        if f'alt_name{i}' not in alt_names_expanded.columns:
            alt_names_expanded[f'alt_name{i}'] = pd.NA
    df = pd.concat([df, alt_names_expanded[[f'alt_name{i}' for i in range(1, 6)]]], axis=1)

    return df

# ---------------------------
# 🧮 Final Processing & Merge
# ---------------------------
def process_hospital_data(df):
    def get_year_opened(row):
        for col in ['Opened', 'year_opened_LLM', 'Established', 'Construction Began']:
            if pd.notnull(row[col]) and 1700 <= row[col] <= 2025:
                return row[col]
        return np.nan

    def get_year_closed(row):
        for col in ['Closed', 'year_closed_LLM']:
            if pd.notnull(row[col]) and 1700 <= row[col] <= 2025:
                return row[col]
        return np.nan

    def get_number_of_beds(row):
        return row['number_of_beds_LLM'] if pd.notnull(row['number_of_beds_LLM']) and row['number_of_beds_LLM'] > 0 else np.nan

    def get_number_of_patients(row):
        for col in ['number_of_patients_LLM', 'peak_patient_population_LLM', 'Peak Patient Population']:
            if pd.notnull(row[col]) and row[col] > 0:
                return row[col]
        return np.nan

    df['hospital_name'] = df['Hospital Name']
    df['city'] = df['City']
    df['final_year_opened'] = df.apply(get_year_opened, axis=1)
    df['final_year_closed'] = df.apply(get_year_closed, axis=1)
    df['final_number_of_beds'] = df.apply(get_number_of_beds, axis=1)
    df['final_number_of_patients'] = df.apply(get_number_of_patients, axis=1)
    df['final_hospital_age'] = df['final_year_closed'] - df['final_year_opened']
    df['hand_check_flag'] = (
        df[['final_year_opened', 'final_year_closed', 'final_number_of_beds', 'final_number_of_patients']]
        .isnull().all(axis=1)
    ).astype(int)

    output_columns = [
        'State', 'city', 'hospital_name', 'alt_name1', 'alt_name2', 'alt_name3', 'alt_name4', 'alt_name5',
        'Hospital_Type', 'URL', 'Current Status', 'Building Style', 'Architecture Style',
        'final_year_opened', 'final_year_closed', 'final_hospital_age',
        'final_number_of_beds', 'final_number_of_patients', 'incomplete_page_flag',
        'kirkbride_flag', 'hand_check_flag'
    ]

    df = df[output_columns]
    df.columns = df.columns.str.lower().str.replace(" ", "_")
    return df

# ---------------------------
# 🛠️ Process Raw CSVs with LLM
# ---------------------------
def extract_llm_data(input_dir, temp_output_dir):
    os.makedirs(temp_output_dir, exist_ok=True)
    csv_files = list(Path(input_dir).glob("*.csv"))

    for csv_file in csv_files:
        df = pd.read_csv(csv_file)
        results = []

        for idx, row in df.iterrows():
            hospital_name = row.get("Hospital Name", "")
            raw_text = row.get("Raw Text", "")
            logging.info(f"Processing {csv_file.name} row {idx+1}/{len(df)}")

            prompt = build_prompt(hospital_name, raw_text)
            response_data = call_openai_api(prompt)

            if response_data:
                results.append(response_data)
            else:
                results.append({
                    "year_opened_LLM": None,
                    "year_closed_LLM": None,
                    "number_of_beds_LLM": None,
                    "number_of_patients_LLM": None,
                    "peak_patient_population_LLM": None,
                    "hand_check_flag_LLM": 1
                })

            time.sleep(1.2)  # Respect rate limit

        # Combine and save intermediate results
        llm_df = pd.DataFrame(results)
        df_combined = pd.concat([df.reset_index(drop=True), llm_df], axis=1)
        df_combined.to_csv(os.path.join(temp_output_dir, f"processed_{csv_file.stem}.csv"), index=False)
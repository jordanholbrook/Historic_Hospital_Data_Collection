import json
import logging
import requests
from config import URL, HEADERS, MODEL

def call_openai_api(prompt):
    data = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "Respond only with a structured Python dictionary based on the user's input."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.15,
        "max_tokens": 1000
    }

    try:
        response = requests.post(URL, headers=HEADERS, json=data)
        if response.status_code == 200:
            content = response.json()["choices"][0]["message"]["content"]
            content_cleaned = content.strip("```json").strip("```").strip()
            return json.loads(content_cleaned)
        else:
            logging.error(f"API Error {response.status_code}: {response.text}")
            return None
    except Exception as e:
        logging.error(f"Exception during API call: {e}")
        return None

def build_prompt(hospital_name, raw_text):
    return f"""
Extract the following information from the hospital history text below:

- year_opened
- year_closed
- number_of_beds
- number_of_patients
- peak_patient_population

In addition, return a field called hand_check_flag. Set hand_check_flag to 1 if:

- The text talks mostly about a different hospital or institution, not the one in this row; OR
- All extracted fields are null.

Otherwise, set hand_check_flag to 0.

Return the result as a JSON object like:
{{
  "year_opened_LLM": [YEAR or null],
  "year_closed_LLM": [YEAR or null],
  "number_of_beds_LLM": [INTEGER or null],
  "number_of_patients_LLM": [INTEGER or null],
  "peak_patient_population_LLM": [INTEGER or null],
  "hand_check_flag_LLM": 0 or 1
}}

---
Hospital Name: {hospital_name}

Text:
\"\"\"{raw_text}\"\"\"
"""

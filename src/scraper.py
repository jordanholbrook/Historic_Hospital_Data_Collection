import requests
import time
import pandas as pd
from bs4 import BeautifulSoup
from typing import Dict
from config import SCRAPFLY_URL, API_KEY, BASE_URL, OUTPUT_DIR
from logger import get_logger

logger = get_logger()

def fetch_html(url: str) -> str:
    """Fetch HTML content from Scrapfly API."""
    params = {"url": url, "key": API_KEY, "format": "raw"}
    try:
        response = requests.get(SCRAPFLY_URL, params=params)
        response.raise_for_status()
        return response.json()["result"]["content"]
    except requests.RequestException as e:
        logger.error(f"Failed to fetch {url}: {e}")
        return ""

def get_state_links() -> pd.DataFrame:
    """Extracts all state page links."""
    url = f"{BASE_URL}/index.php?title=Category:United_States_of_America"
    html_content = fetch_html(url)
    soup = BeautifulSoup(html_content, "html.parser")
    
    state_links = []
    for link in soup.select("div.mw-category-group a"):
        state_name = link.text.strip()
        state_url = f"{BASE_URL}{link['href']}"
        state_links.append((state_name, state_url))
    
    df_states = pd.DataFrame(state_links, columns=["State", "State_URL"])
    df_states.to_csv(f"{OUTPUT_DIR}state_links.csv", index=False)
    logger.info("State links saved.")
    return df_states

def get_hospital_links(state_url: str) -> pd.DataFrame:
    """Extracts hospital links from a state page, filtering out navigation links."""
    html_content = fetch_html(state_url)
    soup = BeautifulSoup(html_content, "html.parser")
    state_name = soup.find("h1", id="firstHeading").text.strip() if soup.find("h1", id="firstHeading") else "Unknown"
    
    hospital_data = []
    for section in soup.find_all("h2"):
        hospital_type = section.text.strip()
        ul = section.find_next("ul")
        
        if ul and "Contents" not in hospital_type and "Navigation menu" not in hospital_type:
            for li in ul.find_all("li"):
                hospital_name = li.text.strip()
                hospital_link = f"{BASE_URL}{li.find('a')['href']}" if li.find("a") else None
                hospital_data.append([state_name, hospital_type, hospital_name, hospital_link])
    
    df_hospitals = pd.DataFrame(hospital_data, columns=["State", "Hospital Type", "Hospital Name", "Hospital Link"])
    df_hospitals.to_csv(f"{OUTPUT_DIR}hospital_links.csv", index=False, mode='a', header=False)
    logger.info(f"Hospital links for {state_name} saved.")
    return df_hospitals

def get_hospital_details(hospital_url: str, state_name: str, max_retries: int, retry_delay: int) -> Dict[str, str]:
    """Extract details of a specific hospital page, including raw text for analysis."""
    attempt, hospital_name = 0, "Unknown"
    hospital_info = {
        "State": state_name,  # Add State Name here
        "Hospital Name": "Unknown",
        "URL": hospital_url,
        "Established": "",
        "Construction Began": "",
        "Opened": "",
        "Current Status": "",
        "Building Style": "",
        "Architect(s)": "",
        "Alternate Names": "",
        "Raw Text": "",
        "Closed": "",
        "Location": "",
        "Architecture Style": "",
        "Peak Patient Population": ""
    }
    
    while attempt < max_retries and hospital_name == "Unknown":
        html_content = fetch_html(hospital_url)
        soup = BeautifulSoup(html_content, "html.parser")
        hospital_name = soup.find("h1", id="firstHeading").text.strip() if soup.find("h1", id="firstHeading") else "Unknown"
        
        if hospital_name != "Unknown":
            hospital_info["Hospital Name"] = hospital_name
            infobox = soup.find("table", class_="infobox Vcard")
            if infobox:
                for row in infobox.find_all("tr"):
                    cells = row.find_all(["th", "td"])
                    if len(cells) == 2:
                        key, value = cells[0].text.strip(), cells[1].text.strip()
                        
                        # Handling multiple alternate names
                        if key == "Alternate Names":
                            value = " | ".join(value.split("\n"))  # Separate multiple names using " | "
                        
                        if key in hospital_info:  # Only add keys that match the predefined columns
                            hospital_info[key] = value
            
            # Extract main text from the page, excluding menus and tables
            content_text = []
            for paragraph in soup.select("#mw-content-text p"):
                text = paragraph.text.strip()
                if text:
                    content_text.append(text)
            
            hospital_info["Raw Text"] = "\n".join(content_text)  # Store raw text for analysis
            
            logger.info(f"Extracted details for {hospital_name}.")
            return hospital_info
        
        logger.warning(f"Retrying {hospital_url}... (Attempt {attempt + 1}/{max_retries})")
        time.sleep(retry_delay)
        attempt += 1
    
    return hospital_info

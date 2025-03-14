import requests
import time
import pandas as pd
from bs4 import BeautifulSoup
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

def get_hospital_details(hospital_url: str) -> dict:
    """Extracts hospital details including raw text content."""
    html_content = fetch_html(hospital_url)
    soup = BeautifulSoup(html_content, "html.parser")
    hospital_name = soup.find("h1", id="firstHeading").text.strip() if soup.find("h1", id="firstHeading") else "Unknown"
    
    hospital_info = {"Hospital Name": hospital_name, "URL": hospital_url, "Raw Text": ""}
    
    # Extract infobox details
    infobox = soup.find("table", class_="infobox Vcard")
    if infobox:
        for row in infobox.find_all("tr"):
            cells = row.find_all(["th", "td"])
            if len(cells) == 2:
                key, value = cells[0].text.strip(), cells[1].text.strip()
                if key == "Alternate Names":
                    value = " | ".join(value.split("\n"))
                hospital_info[key] = value
    
    # Extract main content text
    content_text = [p.text.strip() for p in soup.select("#mw-content-text p") if p.text.strip()]
    hospital_info["Raw Text"] = "\n".join(content_text)
    
    logger.info(f"Extracted details for {hospital_name}.")
    return hospital_info

import pandas as pd
from config import OUTPUT_DIR

def save_to_csv(data: list, filename: str):
    """Appends data to CSV file."""
    df = pd.DataFrame(data)
    df.to_csv(f"{OUTPUT_DIR}{filename}", index=False, header=True) 
    #df.to_csv(f"{OUTPUT_DIR}{filename}", index=False, mode='a', header=False)

import requests
import json
from datetime import datetime, timedelta
import os
from typing import Dict, List
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class ECCCOutlookFetcher:
    BASE_URL = "https://dd.alpha.weather.gc.ca/thunderstorm-outlooks"
    
    def __init__(self):
        self.outlooks_data = {
            "day1": {},  # 12-hour forecasts
            "day2": {},  # 24-hour forecasts
            "day3": {},  # 36-hour forecasts
            "day4": {},  # 60-hour forecasts
            "last_updated": datetime.utcnow().isoformat(),
            "metadata": {
                "source": "Environment and Climate Change Canada",
                "description": "Thunderstorm Outlook Data",
                "update_frequency": "Every 6 hours",
                "regions": {
                    "OSPC": "Ontario Storm Prediction Centre",
                    "QSPC": "Quebec Storm Prediction Centre",
                    "PSPC": "Prairie Storm Prediction Centre (MB, SK, AB)",
                    "ASPC": "Atlantic Storm Prediction Centre (NB, NS, PE, NL)",
                    "BCSPC": "British Columbia Storm Prediction Centre",
                    "PASPC": "Prairie and Arctic Storm Prediction Centre"
                }
            }
        }
        self.successful_fetches = 0
        self.failed_fetches = 0

    def _generate_date_patterns(self) -> List[str]:
        """Generate date pattern for only the current date."""
        today = datetime.utcnow()
        current_date = today.strftime("%Y%m%d")
        
        logging.info(f"Only fetching outlooks for current date: {current_date}")
        return [current_date]

    def _construct_filename_patterns(self) -> List[str]:
        """Construct possible filename patterns for current date only."""
        dates = self._generate_date_patterns()
        regions = [
            ("OSPC", "ON"),   # Ontario
            ("QSPC", "QC"),   # Quebec
            ("PSPC", "BC-YT"), # Prairie - BC/Yukon Territory
            ("ASPC", "NB"),   # Atlantic - New Brunswick
            ("ASPC", "NS"),   # Atlantic - Nova Scotia
            ("ASPC", "PE"),   # Atlantic - Prince Edward Island
            ("ASPC", "NL"),   # Atlantic - Newfoundland and Labrador
            ("BCSPC", "BC"),  # British Columbia
            ("PASPC", "MK"),  # Prairie and Arctic Storm Prediction Centre - Manitoba/SK?
            ("PASPC", "PRAIRIES"), # Prairie and Arctic - All Prairies
        ]
        time_periods = ["PT012H00M", "PT024H00M", "PT036H00M", "PT060H00M"]
        times = ["T1700Z", "T1900Z", "T2000Z"]
        
        patterns = []
        for date in dates:
            for time in times:
                for spc, province in regions:
                    for period in time_periods:
                        base = f"{date}{time}_MSC_ThunderstormOutlook_{spc}_{province}_{period}"
                        # Try multiple versions (v1, v2, v3, v4)
                        for version in range(1, 5):
                            patterns.append(f"{base}_v{version}.json")
        
        logging.info(f"Generated {len(patterns)} possible filename patterns for today")
        return patterns

    def fetch_outlooks(self) -> None:
        """Fetch all available outlook data for the current date only."""
        patterns = self._construct_filename_patterns()
        total_patterns = len(patterns)
        
        logging.info(f"Starting to fetch today's outlook data for {total_patterns} possible patterns")
        
        for index, pattern in enumerate(patterns, 1):
            url = f"{self.BASE_URL}/{pattern}"
            try:
                logging.debug(f"Attempting to fetch: {url}")
                response = requests.get(url, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    self.successful_fetches += 1
                    
                    # Determine which day category this belongs to
                    if "PT012H00M" in pattern:
                        day_key = "day1"
                    elif "PT024H00M" in pattern:
                        day_key = "day2"
                    elif "PT036H00M" in pattern:
                        day_key = "day3"
                    else:  # PT060H00M
                        day_key = "day4"
                    
                    # Extract date and create a unique key for this outlook
                    date = pattern[:8]
                    outlook_key = f"{pattern[:15]}_{pattern.split('_')[3]}_{pattern.split('_')[4]}"  # date_time_spc_province
                    
                    # Initialize the date structure if it doesn't exist
                    if date not in self.outlooks_data[day_key]:
                        self.outlooks_data[day_key][date] = {}
                    
                    # Initialize the outlook structure if it doesn't exist
                    if outlook_key not in self.outlooks_data[day_key][date]:
                        self.outlooks_data[day_key][date][outlook_key] = {
                            "current_version": 0,
                            "outlooks": {}
                        }
                    
                    # Get the version number
                    current_version = int(pattern.split("_v")[-1].split(".")[0])
                    
                    # Only update if this is a newer version
                    if current_version > self.outlooks_data[day_key][date][outlook_key]["current_version"]:
                        self.outlooks_data[day_key][date][outlook_key]["current_version"] = current_version
                        self.outlooks_data[day_key][date][outlook_key]["outlooks"][f"v{current_version}"] = data
                        logging.info(f"Updated to newer version {current_version} for {outlook_key}")
                    
                elif response.status_code == 404:
                    logging.debug(f"File not found: {pattern}")
                    self.failed_fetches += 1
                else:
                    logging.warning(f"Unexpected status code {response.status_code} for {pattern}")
                    self.failed_fetches += 1
                            
            except requests.exceptions.RequestException as e:
                logging.error(f"Error fetching {pattern}: {e}")
                self.failed_fetches += 1
                continue
            
            # Print progress every 20 patterns
            if index % 20 == 0:
                logging.info(f"Progress: {index}/{total_patterns} patterns processed")

    def save_data(self, filename: str = "outlooks_data.json") -> None:
        """Save the fetched data to a JSON file."""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.outlooks_data, f, indent=2)
            logging.info(f"Successfully saved data to {filename}")
            logging.info(f"Summary: {self.successful_fetches} successful fetches, {self.failed_fetches} failed fetches")
        except Exception as e:
            logging.error(f"Error saving data to {filename}: {e}")

def main():
    logging.info("Starting ECCC Thunderstorm Outlook data fetch")
    fetcher = ECCCOutlookFetcher()
    fetcher.fetch_outlooks()
    fetcher.save_data()
    logging.info("Completed ECCC Thunderstorm Outlook data fetch")

if __name__ == "__main__":
    main()

import requests
from bs4 import BeautifulSoup
import json
from typing import List, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FGOScraper:
    def __init__(self):
        self.base_url = "https://fategrandorder.fandom.com"
        self.servant_list_url = f"{self.base_url}/wiki/Servant_List"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def get_basic_servant_data(self) -> List[Dict]:
        """
        Scrape basic servant data (name, class, rarity) from the wiki
        """
        try:
            logger.info("Starting servant data scraping...")
            response = requests.get(self.servant_list_url, headers=self.headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            servants = []
            
            # Find all servant tables (there might be multiple)
            servant_tables = soup.find_all('table', {'class': 'wikitable sortable'})
            
            if not servant_tables:
                logger.error("No servant tables found!")
                # Debug information
                logger.info(f"Found tables: {len(soup.find_all('table'))}")
                logger.info("Page title: " + soup.title.string if soup.title else "No title found")
                return []
            
            logger.info(f"Found {len(servant_tables)} servant tables")
            
            for table in servant_tables:
                # Process each row
                for row in table.find_all('tr')[1:]:  # Skip header row
                    columns = row.find_all(['td', 'th'])
                    
                    if len(columns) >= 3:  # Ensure we have enough columns
                        try:
                            # Extract rarity from the first column's class attribute or star images
                            rarity_col = columns[0]
                            rarity = 0
                            if 'data-sort-value' in rarity_col.attrs:
                                rarity = int(rarity_col['data-sort-value'])
                            else:
                                rarity = len(rarity_col.find_all('img'))
                            
                            # Get name from the second column
                            name_element = columns[1].find('a')
                            if name_element:
                                name = name_element.get_text(strip=True)
                            else:
                                name = columns[1].get_text(strip=True)
                            
                            # Get class from the third column
                            class_element = columns[2].find('a')
                            if class_element:
                                servant_class = class_element.get_text(strip=True)
                            else:
                                servant_class = columns[2].get_text(strip=True)
                            
                            if name and servant_class:  # Only add if we have at least name and class
                                servants.append({
                                    'id': len(servants) + 1,
                                    'name': name,
                                    'class': servant_class,
                                    'rarity': rarity
                                })
                                logger.debug(f"Added servant: {name} ({servant_class}) - {rarity}★")
                        
                        except Exception as e:
                            logger.error(f"Error processing row: {e}")
                            continue
            
            logger.info(f"Successfully scraped {len(servants)} servants")
            
            # Debug: Print first few servants if any were found
            if servants:
                logger.info("First few servants found:")
                for servant in servants[:3]:
                    logger.info(servant)
            
            return servants
            
        except requests.RequestException as e:
            logger.error(f"Error fetching data: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise  # Raise the exception for debugging

    def save_to_json(self, data: List[Dict], filename: str = 'data/servants.json'):
        """Save scraped data to JSON file"""
        try:
            # Ensure the data directory exists
            import os
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"Data saved to {filename}")
        except Exception as e:
            logger.error(f"Error saving data: {e}")
            raise

def main():
    scraper = FGOScraper()
    servants = scraper.get_basic_servant_data()
    if servants:
        scraper.save_to_json(servants)
    else:
        logger.error("No servants were scraped!")

if __name__ == "__main__":
    main()
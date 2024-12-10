import requests
from bs4 import BeautifulSoup
import json
from typing import List, Dict, Optional
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FGOScraper:
    def __init__(self):
        self.base_url = "https://fategrandorder.fandom.com/wiki"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def get_page_url(self, start: int) -> str:
        """Generate URL for each range of servant IDs"""
        end = start + 99
        if start == 1:
            return f"{self.base_url}/Servant_List_by_ID"
        else:
            return f"{self.base_url}/Sub:Servant_List_by_ID/{start}-{end}"

    def scrape_page(self, url: str, max_id: int = 428) -> List[Dict]:
        """
        Scrape a single page of servant data
        max_id: maximum valid servant ID (currently 428)
        """
        try:
            logger.info(f"Scraping URL: {url}")
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            servants = []
            
            # Find the main servant table
            servant_table = soup.find('table', {'class': 'wikitable sortable'})
            if not servant_table:
                logger.error(f"Couldn't find servant table at {url}")
                return []
            
            # Process each row
            for row in servant_table.find_all('tr')[1:]:  # Skip header row
                cells = row.find_all(['td'])
                if len(cells) >= 3:  # We need at least ID and Name columns
                    try:
                        # Get ID from first column
                        servant_id = int(cells[0].get_text(strip=True))
                        
                        # Skip if we've gone past the maximum valid ID
                        if servant_id > max_id:
                            continue
                        
                        # Get name from the third column (Name column)
                        name_cell = cells[2]
                        name_link = name_cell.find('a')
                        name = name_link.get_text(strip=True) if name_link else name_cell.get_text(strip=True)
                        
                        if name:
                            servant_data = {
                                'id': servant_id,
                                'name': name
                            }
                            servants.append(servant_data)
                            logger.info(f"Found servant: {servant_data}")
                    
                    except Exception as e:
                        logger.error(f"Error processing row: {e}")
                        continue
            
            return servants
            
        except requests.RequestException as e:
            logger.error(f"Error fetching data from {url}: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error processing {url}: {e}")
            return []

    def get_all_servant_names(self) -> List[Dict]:
        """Get all servant names across all pages"""
        all_servants = []
        
        # URLs start at 1, then 101, 201, 301, 401
        start_ids = [1, 101, 201, 301, 401]
        
        for start_id in start_ids:
            url = self.get_page_url(start_id)
            servants = self.scrape_page(url)
            all_servants.extend(servants)
            
            # Add a small delay between requests
            time.sleep(1)
        
        # Sort by ID to ensure consistent ordering
        all_servants.sort(key=lambda x: x['id'])
        
        # Verify we got all expected servants
        logger.info(f"Total servants found: {len(all_servants)}")
        if len(all_servants) < 428:
            logger.warning(f"Warning: Only found {len(all_servants)} servants out of 428 expected")
        
        return all_servants

    def save_to_json(self, data: List[Dict], filename: str = 'data/servant_names.json'):
        """Save scraped names to JSON file"""
        try:
            import os
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"Data saved to {filename}")
            logger.info(f"Total servants saved: {len(data)}")
            
            # Print first few and last few entries as a sample
            logger.info("\nFirst few entries:")
            for entry in data[:3]:
                logger.info(entry)
            logger.info("\nLast few entries:")
            for entry in data[-3:]:
                logger.info(entry)
                
        except Exception as e:
            logger.error(f"Error saving data: {e}")
            raise

def main():
    scraper = FGOScraper()
    servants = scraper.get_all_servant_names()
    if servants:
        scraper.save_to_json(servants)
    else:
        logger.error("No servants were scraped!")

if __name__ == "__main__":
    main()
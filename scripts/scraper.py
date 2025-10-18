import time
import pandas as pd
import os
import json
import re
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone

# --- Constants ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "..", "data")
CONFIG_PATH = os.path.join(BASE_DIR, "..", "config.json")
MAX_WORKERS = 2 # 使用一個更穩定的併發數量

# --- Issuer Mapping ---
ISSUER_MAPPING = {
    "yuanta": "元大投信",
    "fubon": "富邦投信",
    "cathay": "國泰投信",
}

def get_selenium_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver

class BaseScraper:
    def __init__(self, etf_code, firm_id):
        self.etf_code = etf_code
        self.firm_id = firm_id

    def scrape(self, driver):
        raise NotImplementedError

class YuantaScraper(BaseScraper):
    def scrape(self, driver):
        scrape_time_utc = datetime.now(timezone.utc)
        etf_url = f"https://www.yuantaetfs.com/product/detail/{self.etf_code}/ratio"
        print(f"Scraping Yuanta ETF {self.etf_code} from {etf_url}...")
        
        driver.get(etf_url)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "mainBox")))
        soup = BeautifulSoup(driver.page_source, 'lxml')
        etf_name = soup.title.string.split("-")[0].strip()

        stock_table_container = next((s for s in soup.find_all('div', attrs={'data-v-818b5120': True}) if (t := s.find('h3')) and '基金權重-股票' in t.text), None)

        if not stock_table_container:
            print(f"-- No stock holdings table found for {self.etf_code}.")
            return None

        rows = stock_table_container.select('.table .tbody .tr')
        holdings_data = []
        for row in rows:
            cols = row.select('.td')
            if len(cols) >= 4:
                code = cols[0].find_all('span')[-1].text.strip()
                name = cols[1].find_all('span')[-1].text.strip()
                shares_text = cols[2].find_all('span')[-1].text.strip()
                weight_text = cols[3].find_all('span')[-1].text.strip()
                if '商品代碼' in code: continue
                holdings_data.append({
                    "code": code, "name": name,
                    "shares": int(shares_text.replace(',', '')), "weight": float(weight_text.strip('%'))
                })

        if not holdings_data:
            print(f"-- No data extracted for {self.etf_code}.")
            return None

        df = pd.DataFrame(holdings_data)
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        output_path = os.path.join(OUTPUT_DIR, f"{self.etf_code}.json")
        output_payload = {
            "last_updated_utc": scrape_time_utc.isoformat(),
            "holdings": df.to_dict(orient='records')
        }
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_payload, f, ensure_ascii=False, indent=4)

        print(f"-- Successfully scraped {len(df)} records for {self.etf_code}.")
        return {"code": self.etf_code, "name": etf_name, "firm_id": self.firm_id, "firm_name": ISSUER_MAPPING.get(self.firm_id, self.firm_id), "last_updated_utc": scrape_time_utc.isoformat()}

class FubonScraper(BaseScraper):
    def scrape(self, driver):
        print(f"-- NOTE: Scraping for Fubon ETF {self.etf_code} is not implemented yet.")
        return None

class CathayScraper(BaseScraper):
    def scrape(self, driver):
        print(f"-- NOTE: Scraping for Cathay ETF {self.etf_code} is not implemented yet.")
        return None

SCRAPERS = {
    "yuanta": YuantaScraper,
    "fubon": FubonScraper,
    "cathay": CathayScraper,
}

def run_scraper_task(target):
    driver = None
    try:
        firm_id = target.get("firm")
        etf_code = target.get("code")
        scraper_class = SCRAPERS.get(firm_id)

        if not scraper_class:
            print(f"-- No scraper available for firm: '{firm_id}'")
            return None

        driver = get_selenium_driver()
        scraper_instance = scraper_class(etf_code, firm_id)
        return scraper_instance.scrape(driver)

    except Exception as e:
        print(f"-- A critical error occurred for {target.get('code')}: {e}")
        return None
    finally:
        if driver:
            driver.quit()

def main():
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            config = json.load(f)
        all_targets = [t for t in config.get("etf_targets", []) if t.get("enabled")]
    except FileNotFoundError:
        print(f"Error: config.json not found at {CONFIG_PATH}")
        return

    args = sys.argv[1:]
    if args:
        targets_to_scrape = [t for t in all_targets if t['code'] in args]
        print(f"Starting targeted scrape for: {[t['code'] for t in targets_to_scrape]}")
    else:
        targets_to_scrape = all_targets
        print(f"Starting full scrape for {len(targets_to_scrape)} enabled ETFs...")

    successful_scrapes = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_etf = {executor.submit(run_scraper_task, target): target for target in targets_to_scrape}
        for future in as_completed(future_to_etf):
            result = future.result()
            if result:
                successful_scrapes.append(result)
    
    if successful_scrapes and not args:
        successful_scrapes.sort(key=lambda x: x['code'])
        manifest_path = os.path.join(OUTPUT_DIR, "etf_list.json")
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(successful_scrapes, f, ensure_ascii=False, indent=4)
        print(f"\nSuccessfully created ETF list manifest for {len(successful_scrapes)} ETFs.")

    print("\nScraping process finished.")

if __name__ == "__main__":
    main()
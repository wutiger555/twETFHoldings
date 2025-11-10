import time
import os
import json
import re
import sys
import csv
import requests
import urllib3
import logging
from typing import List, Dict, Any, Optional, Type
from collections import defaultdict

from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone

# --- Basic Configuration ---
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- Logging Configuration ---
# Suppress verbose logs from webdriver-manager
logging.getLogger('WDM').setLevel(logging.ERROR)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] - [%(threadName)s] - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# --- Constants ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "..", "data")
CONFIG_PATH = os.path.join(BASE_DIR, "..", "config.json")
MAX_WORKERS = 5

# --- Issuer Mapping ---
ISSUER_MAPPING: Dict[str, str] = {
    "yuanta": "元大投信",
    "fubon": "富邦投信",
    "cathay": "國泰投信",
}

def get_selenium_driver() -> WebDriver:
    """Initializes and returns a headless Selenium Chrome WebDriver."""
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver

class BaseScraper:
    """Abstract base class for all ETF scrapers."""
    needs_browser: bool = False

    def __init__(self, etf_code: str, firm_id: str):
        self.etf_code = etf_code
        self.firm_id = firm_id

    def scrape(self, **kwargs: Any) -> Optional[Dict[str, Any]]:
        """The main scraping method to be implemented by subclasses."""
        raise NotImplementedError

class YuantaScraper(BaseScraper):
    """Scraper for Yuanta ETFs, which requires browser interaction."""
    needs_browser = True

    def scrape(self, driver: WebDriver, **kwargs: Any) -> Optional[Dict[str, Any]]:
        etf_url = f"https://www.yuantaetfs.com/product/detail/{self.etf_code}/ratio"
        logging.info(f"Scraping Yuanta ETF {self.etf_code}...")
        
        driver.get(etf_url)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "mainBox")))

        try:
            popup = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.ID, 'outsidePop')))
            driver.execute_script("arguments[0].style.display='none';", popup)
        except TimeoutException:
            pass

        try:
            more_button = WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.CLASS_NAME, 'moreBtn')))
            driver.execute_script("arguments[0].click();", more_button)
            time.sleep(2)
        except TimeoutException:
            pass
        
        soup = BeautifulSoup(driver.page_source, 'lxml')
        etf_name = soup.title.string.split("-")[0].strip()

        stock_table_container = next((s for s in soup.find_all('div', attrs={'data-v-818b5120': True}) if (t := s.find('h3')) and '基金權重-股票' in t.text), None)

        if not stock_table_container:
            logging.warning(f"No stock holdings table found for {self.etf_code}.")
            return None

        rows = stock_table_container.select('.table .tbody .tr')
        holdings_data: List[Dict[str, Any]] = []
        for row in rows:
            cols = row.select('.td')
            if len(cols) >= 4:
                code = cols[0].find_all('span')[-1].text.strip()
                name = cols[1].find_all('span')[-1].text.strip()
                shares_text = cols[2].find_all('span')[-1].text.strip()
                weight_text = cols[3].find_all('span')[-1].text.strip()
                if '商品代碼' in code: continue
                holdings_data.append({
                    "asset_type": "stock",
                    "code": code, "name": name,
                    "shares": int(shares_text.replace(',', '')), "weight": float(weight_text.strip('%'))
                })

        return {"name": etf_name, "holdings": holdings_data}

class FubonScraper(BaseScraper):
    """Scraper for Fubon ETFs, which uses direct HTTP requests."""
    needs_browser = False

    def scrape(self, **kwargs: Any) -> Optional[Dict[str, Any]]:
        etf_url = f"https://websys.fsit.com.tw/FubonETF/Fund/Assets.aspx?stkId={self.etf_code}"
        logging.info(f"Scraping Fubon ETF {self.etf_code}...")

        try:
            response = requests.get(etf_url, timeout=30, verify=False)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'lxml')

            net_asset_value = 0.0
            try:
                asset_list_items = soup.select(".fund_box.p2 ul li")
                for item in asset_list_items:
                    if '基金淨資產(新台幣)' in item.find('p').text:
                        net_asset_value_str = item.find_all('p')[1].text.strip().replace(',', '')
                        net_asset_value = float(net_asset_value_str)
                        break
            except Exception as e:
                logging.warning(f"Could not parse Net Asset Value for {self.etf_code}: {e}. Bond weights will be null.")

            all_holdings: List[Dict[str, Any]] = []
            asset_types: Dict[str, str] = {"股票": "stock", "期貨": "future", "附買回債券": "bond"}

            for asset_name, asset_type_id in asset_types.items():
                heading = soup.find('h6', string=asset_name)
                if heading:
                    table = heading.find_next_sibling('div').find('table')
                    if table:
                        rows = table.find_all('tr')[1:]
                        for row in rows:
                            cols = [c.text.strip() for c in row.find_all('td')]
                            if not cols or len(cols) < 3 or '合計' in cols[0]:
                                continue
                            
                            holding: Dict[str, Any] = {"asset_type": asset_type_id}
                            if asset_type_id == 'stock':
                                holding.update({"code": cols[0], "name": cols[1], "shares": int(cols[2].replace(',', '')), "weight": float(cols[4])})
                            elif asset_type_id == 'future':
                                holding.update({"code": cols[0], "name": cols[1], "shares": int(cols[2].replace(',', '')), "weight": float(cols[4])})
                            elif asset_type_id == 'bond':
                                bond_amount = float(cols[2].replace(',', ''))
                                holding.update({"code": cols[0], "name": cols[1], "shares": None, "weight": (bond_amount / net_asset_value * 100) if net_asset_value > 0 else None})
                            all_holdings.append(holding)

            etf_name = soup.select_one("h5").text.split("/")[1].split("\n")[0].strip() if soup.select_one("h5") else ""
            return {"name": etf_name, "holdings": all_holdings}

        except requests.exceptions.RequestException as e:
            logging.error(f"A critical HTTP error occurred for {self.etf_code}: {e}")
            return None

class CathayScraper(BaseScraper):
    """Placeholder for Cathay ETFs scraper."""
    needs_browser = False
    def scrape(self, **kwargs: Any) -> None:
        logging.info(f"Scraping for Cathay ETF {self.etf_code} is not implemented yet.")
        return None

SCRAPERS: Dict[str, Type[BaseScraper]] = {
    "yuanta": YuantaScraper,
    "fubon": FubonScraper,
    "cathay": CathayScraper,
}

def run_scraper_task(target: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Runs a single scraper task, handles data processing, and saves the output."""
    firm_id = target.get("firm")
    etf_code = target.get("code")
    
    if not firm_id or not etf_code:
        logging.error(f"Invalid target, missing 'firm' or 'code': {target}")
        return None

    scraper_class = SCRAPERS.get(firm_id)
    if not scraper_class:
        logging.warning(f"No scraper available for firm: '{firm_id}'")
        return None

    driver: Optional[WebDriver] = None
    try:
        scraper_instance = scraper_class(etf_code, firm_id)
        
        scrape_kwargs: Dict[str, Any] = {}
        if scraper_class.needs_browser:
            driver = get_selenium_driver()
            scrape_kwargs['driver'] = driver

        scrape_result = scraper_instance.scrape(**scrape_kwargs)

        if not scrape_result or not scrape_result.get("holdings"):
            logging.warning(f"No data returned from scraper for {etf_code}.")
            return None

        # Centralized data processing and file writing
        scrape_time_utc = datetime.now(timezone.utc)
        output_path = os.path.join(OUTPUT_DIR, f"{etf_code}.json")
        holdings = scrape_result["holdings"]
        output_payload = {
            "last_updated_utc": scrape_time_utc.isoformat(),
            "holdings": holdings
        }
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_payload, f, ensure_ascii=False, indent=4)

        logging.info(f"Successfully processed {etf_code} with {len(holdings)} records.")
        
        return {
            "code": etf_code, 
            "name": scrape_result.get("name", ""), 
            "firm_id": firm_id, 
            "firm_name": ISSUER_MAPPING.get(firm_id, firm_id), 
            "holdings_count": len(holdings),
            "status": "success",
            "last_updated_utc": scrape_time_utc.isoformat()
        }

    except Exception as e:
        logging.error(f"A critical error occurred in task runner for {etf_code}: {e}", exc_info=True)
        return {"code": etf_code, "firm_id": firm_id, "status": "failure"}
    finally:
        if driver:
            driver.quit()

# --- Constants ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "..", "data")
LOG_DIR = os.path.join(BASE_DIR, "..", "logs")
CONFIG_PATH = os.path.join(BASE_DIR, "..", "config.json")
MAX_WORKERS = 5

# --- Setup Logging ---
def setup_logging() -> None:
    """Configures logging to output to both console and a timestamped file."""
    os.makedirs(LOG_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_filename = os.path.join(LOG_DIR, f"scrape_run_{timestamp}.log")

    # Get root logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Clear existing handlers
    if logger.hasHandlers():
        logger.handlers.clear()

    # Create file handler
    file_handler = logging.FileHandler(log_filename, encoding='utf-8')
    file_formatter = logging.Formatter(
        '%(asctime)s - [%(levelname)s] - [%(threadName)s] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_formatter = logging.Formatter('[%(levelname)s] - %(message)s')
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # Suppress verbose logs from other libraries
    logging.getLogger('WDM').setLevel(logging.ERROR)
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- Helper Functions ---
def get_display_length(s: str) -> int:
    """Calculates the visual display length of a string, accounting for CJK characters."""
    length = 0
    for char in s:
        if '\u4e00' <= char <= '\u9fff':
            length += 2
        else:
            length += 1
    return length

def generate_summary_report(
    total_duration: float, 
    targets_to_scrape: List[Dict],
    results: List[Dict]
) -> str:
    """Generates a structured, table-like summary report as a string."""
    report_lines = []
    successful_scrapes = [r for r in results if r.get('status') == 'success']
    failed_scrapes = [r for r in results if r.get('status') == 'failure']

    # --- Overall Summary ---
    report_lines.append("\n" + "="*70)
    report_lines.append("SCRAPING SUMMARY".center(70))
    report_lines.append("="*70)
    report_lines.append(f"{'Total Time':<20}: {total_duration:.2f} seconds")
    report_lines.append(f"{'ETFs Processed':<20}: {len(targets_to_scrape)}")
    report_lines.append(f"{'Success':<20}: {len(successful_scrapes)}")
    report_lines.append(f"{'Failure':<20}: {len(failed_scrapes)}")
    report_lines.append("="*70)

    # --- Detailed Breakdown ---
    if results:
        report_lines.append("\n" + "="*70)
        report_lines.append("DETAILED BREAKDOWN".center(70))
        report_lines.append("="*70)

        results_by_issuer: Dict[str, Dict[str, List]] = defaultdict(lambda: {'success': [], 'failure': []})
        for r in results:
            firm_id = r.get('firm_id', 'unknown')
            if r.get('status') == 'success':
                results_by_issuer[firm_id]['success'].append(r)
            else:
                results_by_issuer[firm_id]['failure'].append(r)

        for firm_id, firm_results in sorted(results_by_issuer.items()):
            firm_name = ISSUER_MAPPING.get(firm_id, firm_id)
            success_count = len(firm_results['success'])
            failure_count = len(firm_results['failure'])
            total_count = success_count + failure_count
            status_symbol = "✅" if failure_count == 0 else "🔶" if success_count > 0 else "❌"

            report_lines.append(f"\n{status_symbol} {firm_name} ({firm_id}) - {success_count} / {total_count} ETFs")
            report_lines.append("-"*70)

            if firm_results['success']:
                # Fixed width columns for guaranteed alignment
                CODE_W, HOLD_W, NAME_W = 10, 10, 45
                header = f"  {'Code':<{CODE_W}} {'Holdings':<{HOLD_W}} {'Name':<{NAME_W}}"
                report_lines.append(header)
                report_lines.append(f"  {'-'*CODE_W} {'-'*HOLD_W} {'-'*NAME_W}")
                
                for s in sorted(firm_results['success'], key=lambda x: x['code']):
                    name = s['name']
                    if get_display_length(name) > NAME_W:
                        # Truncate based on display length, not char length
                        name = name[:NAME_W-3] + "..."
                    
                    padding = NAME_W - get_display_length(name)
                    name_padded = name + ' ' * padding
                    report_lines.append(f"  {s['code']:<{CODE_W}} {str(s['holdings_count']):<{HOLD_W}} {name_padded}")

            if firm_results['failure']:
                report_lines.append("\n  Failed ETFs:")
                for f in sorted(firm_results['failure'], key=lambda x: x['code']):
                    report_lines.append(f"  - {f['code']}")
    
    report_lines.append("\n" + "="*70)
    return "\n".join(report_lines)

import io

def update_fund_basic_info() -> bool:
    """Downloads the latest fund basic information CSV and saves it as a JSON file."""
    url = "https://mopsfin.twse.com.tw/opendata/t187ap47_L.csv"
    logging.info(f"Downloading latest fund basic info from {url}...")
    try:
        response = requests.get(url, timeout=30, verify=False)
        response.raise_for_status()
        
        # Decode with utf-8-sig to handle BOM and use StringIO to treat string as a file
        csv_content = response.content.decode('utf-8-sig')
        csv_file = io.StringIO(csv_content)
        
        reader = csv.DictReader(csv_file)
        
        fund_info = {}
        for row in reader:
            fund_code = row.get('基金代號')
            if fund_code:
                fund_info[fund_code.strip()] = row
        
        output_path = os.path.join(OUTPUT_DIR, "fund_basic_info.json")
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(fund_info, f, ensure_ascii=False, indent=4)
        
        logging.info(f"Successfully updated and saved fund_basic_info.json with {len(fund_info)} records.")
        return True
    except Exception as e:
        logging.error(f"Failed to update fund basic info: {e}", exc_info=True)
        return False

# --- Main Execution ---
def main() -> None:
    """Main function to read config, run scrapers, and generate a summary report."""
    setup_logging()
    start_time = time.time()
    logging.info("Scraping process started.")

    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            config = json.load(f)
        all_targets = [t for t in config.get("etf_targets", []) if t.get("enabled")]
    except FileNotFoundError:
        logging.error(f"Configuration file not found at {CONFIG_PATH}")
        return

    args = sys.argv[1:]
    if args:
        targets_to_scrape = [t for t in all_targets if t['code'] in args]
        logging.info(f"Starting targeted scrape for: {args}")
    else:
        targets_to_scrape = all_targets
        logging.info(f"Starting full scrape for {len(targets_to_scrape)} enabled ETFs...")
        # Update basic info only on a full run
        update_fund_basic_info()

    if not targets_to_scrape:
        logging.info("No ETFs enabled or specified for scraping.")
        return

    results: List[Dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS, thread_name_prefix='Scraper') as executor:
        future_to_etf = {executor.submit(run_scraper_task, target): target for target in targets_to_scrape}
        for future in as_completed(future_to_etf):
            try:
                result = future.result()
                if result:
                    results.append(result)
            except Exception as e:
                etf_target = future_to_etf[future]
                logging.error(f"An exception was raised for ETF {etf_target.get('code')}: {e}")
                results.append({"code": etf_target.get('code'), "firm_id": etf_target.get('firm'), "status": "failure"})

    end_time = time.time()
    
    successful_scrapes = [r for r in results if r.get('status') == 'success']
    if successful_scrapes and not args:
        manifest_data = [{
            "code": r['code'], "name": r['name'], "firm_id": r['firm_id'], 
            "firm_name": r['firm_name'], "last_updated_utc": r['last_updated_utc']
        } for r in successful_scrapes]
        manifest_data.sort(key=lambda x: x['code'])
        manifest_path = os.path.join(OUTPUT_DIR, "etf_list.json")
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest_data, f, ensure_ascii=False, indent=4)
        logging.info(f"Successfully created ETF list manifest for {len(manifest_data)} ETFs.")

    # --- Generate and Output Final Report ---
    report_string = generate_summary_report(end_time - start_time, targets_to_scrape, results)
    print(report_string) # Print to console
    logging.info(f"\n{report_string}") # Log to file
    logging.info("Scraping process finished.")

if __name__ == "__main__":
    main()
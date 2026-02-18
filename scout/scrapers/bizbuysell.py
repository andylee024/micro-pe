"""
BizBuySell scraper for building financial benchmarks
"""

import re
import time
from typing import List, Dict, Optional
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def parse_financial(text: str, pattern: str) -> Optional[float]:
    """
    Extract financial value from text using regex

    Args:
        text: Text containing financial data
        pattern: Regex pattern to match

    Returns:
        Parsed financial amount or None
    """
    match = re.search(pattern, text, re.IGNORECASE)
    if not match:
        return None

    # Extract number and suffix (K, M)
    amount_str = match.group(1).replace(',', '')
    amount = float(amount_str)
    suffix = match.group(2) if len(match.groups()) > 1 else ''

    # Apply multiplier
    if suffix.upper() == 'K':
        amount *= 1_000
    elif suffix.upper() == 'M':
        amount *= 1_000_000

    return amount


def setup_driver():
    """
    Setup Chrome driver with anti-detection measures

    Returns:
        Configured WebDriver instance
    """
    try:
        import undetected_chromedriver as uc
        # Use undetected-chromedriver to bypass bot detection
        options = uc.ChromeOptions()
        # Temporarily disable headless to debug
        # options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')

        # Match the installed Chrome version (144)
        driver = uc.Chrome(options=options, version_main=144, use_subprocess=False)
        return driver

    except ImportError:
        # Fallback to regular Selenium with stealth options
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service
        from webdriver_manager.chrome import ChromeDriverManager

        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')

        chromedriver_path = ChromeDriverManager().install()
        # Fix for Mac
        if 'chromedriver-mac' in chromedriver_path:
            import os
            chromedriver_dir = os.path.dirname(chromedriver_path)
            actual_driver = os.path.join(chromedriver_dir, 'chromedriver')
            if os.path.exists(actual_driver):
                chromedriver_path = actual_driver

        service = Service(chromedriver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)

        return driver


def scrape_bizbuysell(industry: str, max_listings: int = 10) -> List[Dict]:
    """
    Scrape BizBuySell for business deals

    Args:
        industry: Industry to search (e.g., "HVAC", "backflow testing")
        max_listings: Maximum number of listings to scrape

    Returns:
        List of deal dictionaries with keys:
        - rank, title, location, revenue, cash_flow, asking_price
        - multiple, margin, url

    Raises:
        Exception: If scraping fails
    """
    driver = setup_driver()
    deals = []

    try:
        # Search page
        search_url = f'https://www.bizbuysell.com/businesses-for-sale/?q={industry.replace(" ", "+")}'
        driver.get(search_url)

        # Wait for results to load
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'a[href*="/business-for-sale/"]'))
            )
        except Exception:
            pass  # Continue anyway

        time.sleep(2)

        # Debug: Save page HTML
        import os
        debug_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'experiments', 'debug_html')
        os.makedirs(debug_dir, exist_ok=True)
        with open(os.path.join(debug_dir, 'bizbuysell_search.html'), 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        print(f"  → Saved page HTML to experiments/debug_html/bizbuysell_search.html")

        # Get listing links - try multiple selectors
        listing_elements = []
        selectors = [
            'a[href*="/business-for-sale/"]',
            'a.listing-link',
            'a.business-card-link',
            '.listing-card a'
        ]

        for selector in selectors:
            listing_elements = driver.find_elements(By.CSS_SELECTOR, selector)
            if listing_elements:
                print(f"  → Found {len(listing_elements)} elements with selector: {selector}")
                break

        if not listing_elements:
            print(f"  → Page title: {driver.title}")
            print(f"  → Current URL: {driver.current_url}")
            raise Exception("Could not find any listing links. Site structure may have changed.")

        # Extract unique URLs
        listing_urls = []
        seen_urls = set()
        for elem in listing_elements:
            url = elem.get_attribute('href')
            if url and '/business-for-sale/' in url and url not in seen_urls:
                listing_urls.append(url)
                seen_urls.add(url)

        listing_urls = listing_urls[:max_listings]

        # Scrape each listing
        for i, listing_url in enumerate(listing_urls, 1):
            try:
                driver.get(listing_url)
                time.sleep(2)

                # Extract text content
                page_text = driver.find_element(By.TAG_NAME, 'body').text

                # Extract title
                try:
                    title = driver.find_element(By.TAG_NAME, 'h1').text
                except:
                    title = 'Unknown'

                # Extract location
                location = 'Unknown'
                try:
                    location_elem = driver.find_element(By.CSS_SELECTOR, '.location, .listing-location, [class*="location"]')
                    location = location_elem.text
                except:
                    pass

                # Extract financials using regex patterns
                revenue = parse_financial(page_text, r'Revenue[:\\s]+\\$?([\\d,\\.]+)\\s*([KMB]?)')
                cash_flow = parse_financial(page_text, r'(?:Cash Flow|EBITDA|SDE)[:\\s]+\\$?([\\d,\\.]+)\\s*([KMB]?)')
                asking_price = parse_financial(page_text, r'Asking Price[:\\s]+\\$?([\\d,\\.]+)\\s*([KMB]?)')

                # Create deal object
                deal = {
                    'rank': i,
                    'title': title,
                    'location': location,
                    'revenue': revenue,
                    'cash_flow': cash_flow,
                    'asking_price': asking_price,
                    'url': listing_url
                }

                # Calculate metrics if we have the data
                if cash_flow and asking_price and cash_flow > 0:
                    deal['multiple'] = round(asking_price / cash_flow, 1)

                if revenue and cash_flow and revenue > 0:
                    deal['margin'] = round(cash_flow / revenue, 2)

                deals.append(deal)

                # Rate limiting
                time.sleep(1)

            except Exception as e:
                print(f"Warning: Error scraping listing {i}: {e}")
                continue

    finally:
        driver.quit()

    return deals


def calculate_benchmarks(deals: List[Dict]) -> Dict:
    """
    Calculate financial benchmarks from scraped deals

    Args:
        deals: List of deal dictionaries

    Returns:
        Dictionary with benchmark statistics
    """
    if not deals:
        return {}

    # Filter to deals with complete financial data
    complete_deals = [
        d for d in deals
        if d.get('revenue') and d.get('cash_flow') and d.get('asking_price')
    ]

    if not complete_deals:
        return {'error': 'No deals with complete financial data'}

    revenues = [d['revenue'] for d in complete_deals]
    cash_flows = [d['cash_flow'] for d in complete_deals]
    multiples = [d['multiple'] for d in complete_deals if d.get('multiple')]
    margins = [d['margin'] for d in complete_deals if d.get('margin')]

    return {
        'total_deals': len(deals),
        'complete_deals': len(complete_deals),
        'revenue': {
            'median': sorted(revenues)[len(revenues) // 2],
            'avg': sum(revenues) / len(revenues),
            'min': min(revenues),
            'max': max(revenues)
        },
        'cash_flow': {
            'median': sorted(cash_flows)[len(cash_flows) // 2],
            'avg': sum(cash_flows) / len(cash_flows),
            'min': min(cash_flows),
            'max': max(cash_flows)
        },
        'multiple': {
            'median': sorted(multiples)[len(multiples) // 2] if multiples else None,
            'avg': sum(multiples) / len(multiples) if multiples else None
        },
        'margin': {
            'median': sorted(margins)[len(margins) // 2] if margins else None,
            'avg': sum(margins) / len(margins) if margins else None
        }
    }

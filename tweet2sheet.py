import os
import re
import json
import time
import yaml
import logging
import gspread
import requests
import feedparser
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from google.oauth2.service_account import Credentials
from typing import List, Dict, Any
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_config():
    try:
        with open('config.yaml', 'r') as config_file:
            config = yaml.safe_load(config_file)
        logger.debug("Config file loaded successfully")
        return config
    except FileNotFoundError:
        logger.error('Configuration file (config.yaml) not found.')
        exit(1)
    except yaml.YAMLError as e:
        logger.error(f'Error parsing YAML configuration: {e}')
        exit(1)

def initialize_google_sheets(config):
    try:
        credentials = config['google_credentials']
        logger.debug(f"Credentials keys: {list(credentials.keys())}")
        
        # Check for required keys
        required_keys = ['type', 'project_id', 'private_key_id', 'private_key', 'client_email', 'client_id']
        missing_keys = [key for key in required_keys if key not in credentials]
        if missing_keys:
            logger.error(f"Missing required keys in credentials: {missing_keys}")
            exit(1)
        
        # Preprocess the private key
        if 'private_key' in credentials:
            credentials['private_key'] = credentials['private_key'].replace('\\n', '\n')
            logger.debug("Private key preprocessed")
        else:
            logger.error("Private key is missing from credentials")
        
        # Use service_account_from_dict instead of authorize
        gc = gspread.service_account_from_dict(credentials)
        logger.debug("Google Sheets client initialized successfully")
        return gc
    except KeyError:
        logger.error('Google credentials not found in config file.')
        exit(1)
    except Exception as e:
        logger.error(f'Error initializing Google Sheets client: {e}')
        logger.exception("Full traceback:")
        exit(1)

def open_google_sheet(gc, config):
    try:
        SHEET_URL = config['master_config_url']
        if not SHEET_URL:
            raise ValueError("master_config_url is empty")
        logger.debug(f"Google Sheet URL loaded: {SHEET_URL}")
        
        sh = gc.open_by_url(SHEET_URL)
        worksheet = sh.sheet1
        
        # Check if the sheet is empty and add column names if it is
        if worksheet.row_count == 0:
            column_names = config.get('column_names', [])
            if not column_names:
                logger.error("Column names not found in config file")
                exit(1)
            worksheet.append_row(column_names)
            logger.info("Added column names to the empty sheet")
        
        logger.debug("Successfully opened Google Sheet")
        return worksheet
    except KeyError:
        logger.error('master_config_url not found in config file.')
        exit(1)
    except ValueError as e:
        logger.error(f'Invalid master_config_url: {e}')
        exit(1)
    except Exception as e:
        logger.error(f'Error accessing Google Sheet: {e}')
        logger.exception("Full traceback:")
        exit(1)

def fetch_html_content(url: str) -> str:
    try:
        start_time = time.time()
        response = requests.get(url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        duration = round(time.time() - start_time, 2)
        logger.info(f"Fetched content from {url} in {duration} seconds.")
        return response.text
    except requests.RequestException as e:
        logger.error(f"Error fetching content from {url}. Error: {e}")
        return None

def check_for_tweets(html: str) -> List[str]:
    tweet_urls = re.findall(r'https?://(?:www\.)?(?:twitter\.com|x\.com)/\w+/status/\d+', html)
    return list(set(tweet_urls))

def format_domain(url: str) -> str:
    domain = url.split("//")[-1].split("/")[0]
    domain = re.sub(r'^www\.', '', domain)
    domain = re.sub(r'\.no$', '', domain)
    return domain

def process_entry(entry: Dict[str, Any], processed_urls: set, processed_tweets: set) -> List[List[str]]:
    url = entry.get('link')
    if not url or url in processed_urls:
        return []
    processed_urls.add(url)

    # Check if the entry is too old
    published_date = entry.get('published_parsed')
    if published_date:
        entry_age = datetime.now() - datetime(*published_date[:6])
        if entry_age > MAX_AGE:
            logger.info(f"Skipping old entry: {url}")
            return []

    html = fetch_html_content(url)
    if not html:
        return []

    tweets = check_for_tweets(html)
    if not tweets:
        return []

    logger.info(f"Found {len(tweets)} tweets in the URL: {url}")

    rows = []
    for tweet in tweets:
        if tweet in processed_tweets:
            continue
        processed_tweets.add(tweet)

        now = datetime.now()
        row = [
            now.strftime("%Y-%m-%d"),  # Date
            now.strftime("%H:%M:%S"),  # Time
            format_domain(url),  # Domain
            tweet.split("/")[-3],  # Twitter Handle
            url,  # Article URL
            tweet,  # Tweet URL
            entry.get('title', ''),  # Article Title
            entry.get('summary', ''),  # Article Summary
            entry.get('published', ''),  # Published Date
            str(len(tweets))  # Tweet Count
        ]
        rows.append(row)

    return rows

def append_to_sheet(worksheet, rows):
    try:
        worksheet.append_rows(rows, value_input_option='RAW', insert_data_option='INSERT_ROWS')
        logger.info(f"Added {len(rows)} new entries to the sheet")
    except Exception as e:
        logger.error(f"Error appending rows to Google Sheet: {e}")
        # Implement retry logic here if needed

def main():
    config = load_config()
    gc = initialize_google_sheets(config)
    worksheet = open_google_sheet(gc, config)
    
    global FEEDS, MAX_WORKERS, REQUEST_TIMEOUT, RATE_LIMIT, MAX_AGE
    
    FEEDS = config.get('rss_feeds', [])
    if not FEEDS:
        logger.error('No RSS feeds found in configuration file.')
        exit(1)

    MAX_WORKERS = config.get('max_workers', 10)
    REQUEST_TIMEOUT = config.get('request_timeout', 10)
    RATE_LIMIT = config.get('rate_limit', 1)  # requests per second
    MAX_AGE = timedelta(days=config.get('max_age_days', 7))
    
    processed_urls = set()
    processed_tweets = set()
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_feed = {executor.submit(feedparser.parse, feed_url): feed_url for feed_url in FEEDS}
        for future in as_completed(future_to_feed):
            feed_url = future_to_feed[future]
            try:
                feed = future.result()
                logger.info(f"Scanning feed: {feed_url}")
                logger.info(f"Found {len(feed.entries)} entries in the feed.")
                
                all_rows = []
                entry_futures = [executor.submit(process_entry, entry, processed_urls, processed_tweets) for entry in feed.entries]
                for entry_future in as_completed(entry_futures):
                    rows = entry_future.result()
                    if rows:
                        all_rows.extend(rows)
                    time.sleep(1 / RATE_LIMIT)  # Rate limiting

                if all_rows:
                    append_to_sheet(worksheet, all_rows)
            except Exception as exc:
                logger.error(f'{feed_url} generated an exception: {exc}')
    
    logger.info(f'Finished scanning all feeds. Scanned {len(processed_urls)} URLs, found {len(processed_tweets)} new tweets.')

if __name__ == '__main__':
    main()

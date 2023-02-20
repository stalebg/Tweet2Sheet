import requests
import feedparser
import gspread
import google.oauth2
from google.oauth2 import service_account
from google.oauth2.credentials import Credentials
from bs4 import BeautifulSoup
from datetime import datetime

# Dictionary of Google credentials
credentials = {
  "type": "ACCOUNT TYPE",
  "project_id": "PROJECT NAME",
  "private_key_id": "PRIVATE KEY",
  "private_key": "-----BEGIN PRIVATE KEY-----LONG KEY-----END PRIVATE KEY-----",
  "client_email": "ACCOUNT EMAIL",
  "client_id": "NUMBER",
  "auth_uri": "AUTH-URL",
  "token_uri": "TOKEN-URL",
  "auth_provider_x509_cert_url": "AUTH-PROVIDER-URL",
  "client_x509_cert_url": "CLIENT-CERT-URL"
}

# List of RSS feed URLs
feeds = [
    'https://www.theguardian.com/world/rss',
    'http://feeds.bbci.co.uk/news/world/rss.xml',
]

# Authorize and access the Google Sheet
gc = gspread.service_account_from_dict(credentials)
sheet_link = "URL TO YOUR SPREADSHEET"
sh = gc.open_by_url(sheet_link)
worksheet = sh.sheet1

# Function to check for tweets in HTML
def check_for_tweets(html):
    soup = BeautifulSoup(html, 'html.parser')
    tweets = []
    for a in soup.find_all('a', href=True):
        if '/status/' in a['href']:
            tweets.append(a['href'])
    return tweets

# Function to write to Google Sheets
def write_to_google_sheets(tweet, url, domain, current_date, current_time, username):
    row = [current_date, current_time, domain, username, url, tweet]
    # Check for duplicates
    for i, existing_row in enumerate(worksheet.get_all_values()):
        if i == 0:  # skip header row
            continue
        if existing_row[4] == row[4] and existing_row[5] == row[5]:
            print(f'Skipping duplicate row: {row}')
            return
    # Add new row to worksheet
    worksheet.append_row(row)
    print(f'New tweet found: {tweet}')

# Sets to keep track of already processed tweets and urls
processed_tweets = set()
processed_urls = set()

# Loop through RSS feeds
for feed_url in feeds:
    print(f'Scanning feed: {feed_url}')
    feed = feedparser.parse(feed_url)
    for entry in feed.entries:
        url = entry.link
        domain = url.split('//')[-1].split('/')[0]
        print(f'Checking url: {url}')

        # Skip if URL has already been processed
        if url in processed_urls:
            continue
        processed_urls.add(url)
        # Get HTML from URL
        try:
            response = requests.get(url)
            response.raise_for_status()
            html = response.text
        except requests.exceptions.RequestException as e:
            print("Error: ", e)

        # Check for tweets in HTML
        tweets = check_for_tweets(html)
        # Write tweets to Google Sheets
        for tweet in tweets:
            # Skip if tweet has already been processed
            if tweet in processed_tweets:
                continue
            processed_tweets.add(tweet)
            now = datetime.now()
            current_date = now.strftime("%Y-%m-%d")
            current_time = now.strftime("%H:%M:%S")
            username = tweet.split("/")[-3]
            write_to_google_sheets(tweet, url, domain, current_date, current_time, username)

print(f'Finished scanning {len(processed_urls)} URLs, found {len(processed_tweets)} new tweets.')
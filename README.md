# Tweet2Sheet :bird: :page_facing_up:

![GitHub](https://img.shields.io/github/license/stalebg/Tweet2Sheet)
![Heroku](https://img.shields.io/badge/Heroku-purple?logo=heroku&amp;logoColor=white)
![Python](https://img.shields.io/badge/Python-3.7%2B-blue?logo=python&logoColor=white)

Tweet2Sheet is a Python-based application that scans URLs from RSS feeds and identifies embedded tweets or tweet links. These are then extracted and logged into a Google Spreadsheet for easy access and review.

## :star2: Features

- **Scans RSS Feeds**: Utilizes Feedparser to scan and extract URLs from RSS feeds.
- **Extracts Tweets**: Employs BeautifulSoup to scan URLs and detect embedded or linked tweets.
- **Outputs to Google Spreadsheet**: Stores all identified tweets into a Google Spreadsheet.
- **Ignores Duplicate Entries**: When run multiple times, the script disregards duplicate entries, ensuring a unique collection of tweets.
- **Configurable Columns**: Easily customize the columns in your Google Sheet via the config file.
- **Domain Formatting**: Automatically formats domain names for consistency (removes 'www.' and '.no').

## :page_with_curl: Output Format

The output Google Spreadsheet contains the following columns:

| Date | Time | Domain | Twitter Handle | Article URL | Tweet URL | Article Title | Article Summary | Published Date | Tweet Count |
|------|------|--------|----------------|-------------|-----------|---------------|-----------------|----------------|-------------|
|      |      |        |                |             |           |               |                 |                |             |

## :gear: Configuration

The application uses a YAML configuration file (`config.yaml`) for easy setup and customization. Here's an example structure:

```yaml
google_credentials:
  # Your Google Sheets API credentials here

master_config_url: "https://docs.google.com/spreadsheets/d/your-spreadsheet-id/edit#gid=0"

rss_feeds:
  - "https://example.com/feed1.rss"
  - "https://example.com/feed2.rss"

column_names:
  - Date
  - Time
  - Domain
  - Twitter Handle
  - Article URL
  - Tweet URL
  - Article Title
  - Article Summary
  - Published Date
  - Tweet Count

max_workers: 10
request_timeout: 10
rate_limit: 1
max_age_days: 7
```

## :rocket: Deployment on Heroku

The repository includes all necessary files to clone and run the project as an app on Heroku. You just need to update the `config.yaml` file with your Google account details. If you're unfamiliar with this process, follow the steps outlined in [this tutorial](https://aryanirani123.medium.com/read-and-write-data-in-google-sheets-using-python-and-the-google-sheets-api-6e206a242f20).

## :closed_lock_with_key: Credentials

Credentials are required for Google Sheets API access. These should be placed in the `config.yaml` file. You can obtain these credentials from your Google account (a json-file will be provided by Google). For details on how to obtain and use these credentials, refer to the above-mentioned tutorial.

After obtaining the json-file, copy the credentials into the `config.yaml` file before running the script. Always be mindful to keep such credentials secure and do not share them publicly.

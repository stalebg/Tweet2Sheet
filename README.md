# Tweet2Sheet :bird: :page_facing_up:

![GitHub](https://img.shields.io/github/license/stalebg/Tweet2Sheet)

Tweet2Sheet is a Python-based application that scans URLs from RSS feeds and identifies embedded tweets or tweet links. These are then extracted and logged into a Google Spreadsheet for easy access and review.

## :star2: Features
- **Scans RSS Feeds**: Utilizes Feedparser to scan and extract URLs from RSS feeds.
- **Extracts Tweets**: Employs BeautifulSoup to scan URLs and detect embedded or linked tweets.
- **Outputs to Google Spreadsheet**: Stores all identified tweets into a Google Spreadsheet.
- **Ignores Duplicate Entries**: When run multiple times, the script disregards duplicate entries, ensuring a unique collection of tweets.

The output Google Spreadsheet contains the following columns:

| current_date  |  current_time | domain  | username  | url  | tweet  |
| ------------ | ------------ | ------------ | ------------ | ------------ | ------------ |
|   |   |   |   |   |   |

## :rocket: Deployment on Heroku
The repository includes all necessary files to clone and run the project as an app on Heroku. You just need to update the script with your Google account details. If you're unfamiliar with this process, follow the steps outlined in [this tutorial](https://aryanirani123.medium.com/read-and-write-data-in-google-sheets-using-python-and-the-google-sheets-api-6e206a242f20).

## :closed_lock_with_key: Credentials
Credentials are required for Google Sheets API access. These are currently listed as a dictionary within the script. You can obtain these credentials from your Google account (a json-file will be provided by Google). For details on how to obtain and use these credentials, refer to the above-mentioned tutorial.

After obtaining the json-file, simply copy the credentials and paste them into the script before running it (And always be mindful to keep such credentials secure and do not share them out in the open).

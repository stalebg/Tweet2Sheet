# Tweet2Sheet
Scans URLs in RSS feeds looking for embeds of, or links to, tweets. Outputs these to a Google Spreadsheet with the columns:

| current_date  |  current_time | domain  | username  | url  | tweet  |
| ------------ | ------------ | ------------ | ------------ | ------------ | ------------ |
|   |   |   |   |   |   | |


It scans RSS feeds with Feedparser and extracts entry's URLs. Scans them for tweets with BeautifulSoup. Any URLs with tweets found in them will be output to a Google Sheet. Duplicate entries disregarded when the script is run repeatedly.

# Run on Heroku
Files included makes it possible to clone and run as an app on Heroku. Just update the script with your Google details (Follow i.e. the steps outlined in [this tutorial](https://aryanirani123.medium.com/read-and-write-data-in-google-sheets-using-python-and-the-google-sheets-api-6e206a242f20 "this tutorial")) .

# Credentials
Currently listed as a dictionary in the script itself. Just copy the credentials from the json-file Google gives you (see above mentioned tutorial), and paste them into the script before you run it.

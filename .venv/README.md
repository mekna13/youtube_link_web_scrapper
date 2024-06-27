

# Youtube Link Scrapper 

## Description

The department I was working with in the university was transitioning to a new YouTube channel, there was a need to update 
all links and embedded videos from the old channel to the new one. Since there were more than a hundred links on the site
I needed to check whether the links have been currently updated.

## Purpose
The primary goal of this project is to automate the process of checking whether the YouTube links on the CMS site 
have been updated. 
The task involves:

1. Scraping the entire CMS site to locate all YouTube video links.
2. Verifying whether each linked video belongs to the new, correct YouTube channel.
3. Recording all relevant information about the links into an Excel sheet for further analysis and tracking.

## Getting Started

### Dependencies

The project uses the following python packages
* re
* json
* requests
* BeautifulSoup
* xlsxwriter
* dotenv 


### Executing program
Run the main.py file to execute the program.
```
python main.py
```

## Environment Variables

Create a .env files with the following variables
```
CHANNEL_ID='XXXXXXXXXXXX'
CHANNEL_NAME='XXXXXXXXXXXX'
BASE_URL='https://example.com'
```

## Output
The script should produce an excel file called Testing_Youtube_Links.xlsx that contains
the information of the pages that were not updated specifically the page url, the html tag, 
the channel id and the channel name





# Food-Recipe-Scraping
Hello guys! I'm Han Sheng. Passionate in Artificial Intelligent (Data Science, Internet of Things, Image Processing etc).
I developed one program where can scrap data from one website and store into SQLite database.
Welcome to give contribution/suggestion to my project!

## Data Source
1. https://www.allrecipes.com/

## Steps
1. Run spider.py to crawl all the available links in the website. It might take few hours to crawl all the data. We can scrap it multiple times since this script will continue from where we stop last time.
2. Run clean_scrap.py to filter the links, extract the data from the page and save into SQLite database.
3. Download Sqlite Browser from https://sqlitebrowser.org/ to open the database and preview the data scraped from pages.


# Notics 
 This project fork from https://github.com/hansheng0512/Food-Recipe-Scraping/
 I try to build a sqlite class which easy manage the and reusable to other python script.
 I implement the sys argument which is base on specify the content form json key to proceed the tasks. The format:
 python.exe .\spider.py allrecipes sqlite

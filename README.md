# Web Scraping Singapore Pools

## What is this doing?
This is a web scraping bot that uses selenium to web scrap 2 filters in https://online.singaporepools.com/en/sports and web scrape the bets and calculate
implied probability of each bet. This is so that we can find arbitrage betting opportunities. If implied probability is more than 100% its in their odds, 
if its less than 100% its in the better's odds. Singapore Pools is heavily in the website's odds thus its highly unlikely that there will be arbitrage 
betting opportunities.

## How to run.
To run this bot. You would need to install all the required packages
- Selenium
- Pandas
Once run, the bot will run and will export the data in the form of 2 csv files.

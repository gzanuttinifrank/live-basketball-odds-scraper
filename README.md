# live-basketball-odds-scraper

This script scrapes Bovada's live basketball odds section roughly every 15 seconds, collecting all available information about each game from the top level in addition to the moneyline odds (in European format), creates a unique ID for each game, and records the time of execution.

The following is an example of the output:
![Sample of scraped data](https://github.com/gzanuttinifrank/live-basketball-odds-scraper/blob/master/sample_scraped_data.png)

The datasets in this repository are from the period between 12/05/19 and 12/19/19. They are not comprehensive (the script was not running continously for that entire time frame). **basketball_live_odds_bovada.csv** contains the raw output, while **basketball_live_odds_bovada_cleaned.csv** was cleaned to an extent, fixing various issues resulting primarily from issues with Bovada's website and the information displayed.

I personally have a much more extensive dataset that I am willing to share with anyone.

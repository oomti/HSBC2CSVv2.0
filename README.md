## HSBC PDF scraping script v2

This script has been created to scrape HSBC statements.

HSBC statements are scraped into CSV format.

Use
Activate the virtual environment(dependencies included in the package), scripts for virtual environment are in the scripts folder

>python main.py --input <"location and name of your statement"> --output <"the csv/emptyfile/new file you want to append the results to">

Example

>python main.py --input HSBC_January_2020.pdf --output records_2020.csv
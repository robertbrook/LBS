#!/usr/local/bin/python3

import re
import csv
import requests
from bs4 import BeautifulSoup

page = {}

url = "https://lordsbusiness.parliament.uk/?businessPaperDate=2020-05-12"

r = requests.get(url)

soup = BeautifulSoup(r.text, "html.parser")

# date_string = soup.select_one("#main > div > div.col-md-9.section > h3 > span").string
# 
# page["date_string"] = date_string

page["business_items"] = []

def get_business_items(with_soup):
    items_of_business = with_soup.select( "div.items-of-business-list > .item-of-business" )
    for item_of_business in items_of_business:
        item_of_business_href = item_of_business.get('href')
        item_of_business_text = item_of_business.select_one('div.truncate').get_text()
        match = re.search(r'\/ItemOfBusiness\?itemOfBusinessId=(\d*)&sectionId=(\d*)&businessPaperDate=(\d\d\d\d-\d\d-\d\d)', item_of_business_href)        
        page["business_items"].append([match[1], match[2], match[3], item_of_business_text])
        
    with open('items.csv', 'a', newline='') as csvfile:
        itemwriter = csv.writer(csvfile)            
        itemwriter.writerows(page["business_items"])
        
business_paper_date = soup.select_one(
    "#main > div > div.col-md-3.business-paper-options > div.date-select > div.date-controls > div.datepicker > input.form-control"
)

business_paper_date_parts = business_paper_date["value"].split()[0].split("/")

business_paper_date_parts.reverse()

url_date = "-".join(business_paper_date_parts)

page["url_date"] = url_date

def process_section(with_url_date, with_section_value):
    section_url = "https://lordsbusiness.parliament.uk/?businessPaperDate=" + with_url_date + "&sectionId=" + with_section_value
    section_request = requests.get(section_url)
    section_soup = BeautifulSoup(section_request.text, "html.parser")
    get_business_items(section_soup)

page["sections"] = []

sections = soup.select(
    "#main > div > div.col-md-3.business-paper-options > div.section-select > div.section-select-mobile > select.form-control > option"
)

for section in sections:
    page["sections"].append([section.string, section["value"]])    
    section_url = "https://lordsbusiness.parliament.uk/?businessPaperDate=" + url_date + "&sectionId=" + section["value"]
    section_request = requests.get(section_url)
    section_soup = BeautifulSoup(section_request.text, "html.parser")
    get_business_items(section_soup)
    
print(f"processed {url} into items.csv")

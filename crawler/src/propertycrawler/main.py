'''
@File: main.py
@Time: 05.12.2025 17:16:41
@Author: Karri Korsu 
@Version : 1.0
@Contact : kkorsu@gmail.com
@Desc: None
'''
from sys import argv
from remax import Remax
from cli import argparser
from datahandler import IO
from parser import JsonParser
from crawler import Crawler
if __name__ == "__main__":
    args = argparser(argv[1:])

    remax = Remax()
    url = "https://remax.fi/wp-content/themes/blocksy-child/property_search_LINEAR.php?property-type=asunnot&realty-type=&bedrooms=&showings-from=&showings-to=&location=turku&price_min=&price_max=&living_area_m2_min=&living_area_m2_max=&lot_area_min=&lot_area_max=&buildyear_min=&buildyear_max=&location=turku&page=15"
    remax.php_query_url = args.url
    io = IO()
    listings = io.get_json("data/property_search_LINEAR.php.html")
    print(listings)
    json = JsonParser(listings)
    print('getting ids')
    ids = json.get_ids()
    remax.populate_listing_list(ids)
    # add session id!
    session ="today+site"
    print(remax.listings)
    crawler = Crawler()
    for item in remax.listings:
        #crawler.get_listing_page(remax.Listing.url, item.id) #tested functionally, works 
        print(crawler.get_listing_list_page(url))
        break






        


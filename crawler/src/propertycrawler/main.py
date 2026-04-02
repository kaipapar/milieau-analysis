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
    """ 
     1. Enter URL as CLI input (direct link to public content for now)
     2. Initialize correct PropertySite implementation class
     3. Start crawling: surf to url and download contents
     4. Convert /interpret the contents to/as JSON
     5. Extract listing IDs from the JSON and generate a set from them
     6. Create Listing type objects from the set
     7. Surf to each listing's page and download as HTML
     8. Parse to extract features from the HTML to corresponding listing object
     9. Pass all listing objects to a dataframe
     ... TODO check for duplicate addresses in current data and previously generated data 
            -> minimizes geocoding requests
     10. Geocode each listing address and add to dataframe
     ... TODO Add session id to each
     ... TODO add site id to each
     11. Save dataframe as CSV
     12. Voilá
        """
    args = argparser(argv[1:])

    # initialize class instances
    remax = Remax()

    # set the url from cli arguments as the url to be used
    remax.php_query_url = args.url

    # add session id! TODO
    session ="today+site"

    ## for functional testing
    url = "https://remax.fi/wp-content/themes/blocksy-child/property_search_LINEAR.php?property-type=asunnot&realty-type=&bedrooms=&showings-from=&showings-to=&location=turku&price_min=&price_max=&living_area_m2_min=&living_area_m2_max=&lot_area_min=&lot_area_max=&buildyear_min=&buildyear_max=&location=turku"
    
    listings = IO.get_json("data/property_search_LINEAR.php.html")
    print(listings)
    ## 

    # process the retrieved json containing the listings into a more compact set of Listing objects
    json = JsonParser(listings)
    print('getting ids')
    ids = json.gen_id_set()
    remax.populate_listing_list(ids)

    print(remax.listings)
    for item in remax.listings:
        #crawler.get_listing_page(remax.Listing.url, item.id) #tested functionally, works 
        print(Crawler.get_listing_list_page(url))
        break






        


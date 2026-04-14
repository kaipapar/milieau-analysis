'''
@File: main.py
@Time: 05.12.2025 17:16:41
@Author: Karri Korsu 
@Version : 1.0
@Contact : kkorsu@gmail.com
@Desc: None
'''
from sys import argv
from propertycrawler.remax import Remax
from propertycrawler.cli import argparser
from propertycrawler.datahandler import IO
from propertycrawler.parser import JsonParser
from propertycrawler.parser import HtmlParser
from propertycrawler.datahandler import DF
from propertycrawler.datahandler import GC
from propertycrawler.crawler import Crawler
from propertycrawler.constants import REMAX_ATTR_KEYS
import pandas as pd
from datetime import datetime
import pathlib


def main():
    """ Main crawler execution function """
    args = argparser(argv[1:])
    # initialize class instances
    remax = Remax()
    # set the url from cli arguments as the url to be used
    remax.php_query_url = args.url

    # Generate site ID and session ID for organizing output files
    site_id = remax.__class__.__name__.lower()  # e.g., "remax"
    session_id = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")  # e.g., "2026-04-09_14-30-45"
    base_data_path = f"./data/{site_id}/{session_id}/"
    
    print(f"Starting crawl session: site_id={site_id}, session_id={session_id}")
    print(f"Output directory: {base_data_path}")

    ## for functional testing
    #url = "https://remax.fi/wp-content/themes/blocksy-child/property_search_LINEAR.php?property-type=asunnot&realty-type=&bedrooms=&showings-from=&showings-to=&location=turku&price_min=&price_max=&living_area_m2_min=&living_area_m2_max=&lot_area_min=&lot_area_max=&buildyear_min=&buildyear_max=&location=turku"

    """ 
    listings = IO.get_json("data/property_search_LINEAR.php.html")
    print(listings) """
    ## 

    # filepath should be specified to sessionID
    listing_list_path = pathlib.Path(base_data_path) / "listing_lists"
    Crawler.get_listing_list_full(url=remax.php_query_url, filepath=str(listing_list_path))
    # Create parser instance and retrieve all IDs from all pages on disk
    json = JsonParser([])  # Start with empty list, will be updated per page
    all_ids = Crawler.get_listing_ids_from_disk(filepath=str(listing_list_path), parser=json)
    # process the retrieved json containing the listings into a more compact list of Listing objects
    remax.populate_listing_list(all_ids)
    print(remax.listings)

    # Download individual listing pages to session directory
    listings_path = pathlib.Path(base_data_path) / "listings"
    Crawler.get_listings(remax, filepath=str(listings_path))
    HtmlParser.parse_listings(remax.listings)
    
    # Create dataframe with proper column structure
    dataset = pd.DataFrame(columns=REMAX_ATTR_KEYS)
    # Add all listing rows to dataframe (this includes siteID, sessionID, and listingID)
    dataset = DF.add_rows(dataset, remax.listings, session_id)
    # try to geocode all
    GC.geocode_all(dataset, REMAX_ATTR_KEYS[0]) # [0] == "Osoite: "
    # Save to CSV in the session directory
    csv_path = pathlib.Path(base_data_path) / f"{site_id}_{session_id}.csv"
    print(f"***Geocoding done. Printing generated dataset and saving to disk at: \n {str(csv_path)} \n {dataset}")
    DF.save(dataset, str(csv_path))


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
     11. Save dataframe as CSV
     12. Voilá
        """
    main()







        


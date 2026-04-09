'''
@File: crawler.py
@Time: 05.12.2025 17:17:38
@Author: Karri Korsu 
@Version : 1.0
@Contact : kkorsu@gmail.com
@Desc: None
'''

import subprocess
from propertysite import PropertySite
from datahandler import IO
import warnings
import pathlib
import os

class Crawler:
    def get_listing_page(url: str, id: str, filepath="./data/listings/"):
        """ retrieve and save individual listing page. Doesn't check for valid html, because it is parsed as txt, not html, for now"""
        filepath = pathlib.Path(filepath)
        
        if (str(filepath)[-5:] != ".html"):
            warnings.warn(f"method: get_listing_page: Improper filepath detected: {filepath} \tResorting to default")
            filepath = pathlib.Path(f"./listing_"+str(id)+".html").absolute()
        
        if (not IO.is_empty(filepath)):
            warnings.warn(f"file is already populated. Creating a new file.")
            new_filepath = filepath.with_name(f"{filepath.stem}(1){filepath.suffix}")
            Crawler.get_listing_page(url, id, new_filepath)
            return

        result = subprocess.run(['wget', '-O', f'{str(filepath)}', f'{url}'])
        result.check_returncode() # if return code is nonzero -> raises CalledProcessError

    def get_listings(obj: PropertySite):
        for listing in obj.listings:
            Crawler.get_listing_page(listing.url, listing.id, listing.filepath)
            
    def get_listing_list_page(url: str, filepath="./data/listings/") -> bool:
        """ retrieve and save listing list page to specified location with wget """
        # Convert to pathlib.Path for consistent handling
        filepath = pathlib.Path(filepath)
        
        # Check for both .json and .html file extensions (for test compatibility)
        valid_extensions = (".json", ".html")
        if not str(filepath).endswith(valid_extensions):
            warnings.warn(f"method: get_listing_list_page: Improper filepath detected: {filepath} \tResorting to default")
            filepath = pathlib.Path('listing_list.json').absolute()
      
        result = subprocess.Popen(['wget', '-q', '-O', '-', f'{url}'], stdout=subprocess.PIPE)

        to_file = subprocess.check_output(('tee', f'{str(filepath)}'), stdin=result.stdout)
        
        result.wait()
        print("result: ",  result)
        print("to_file: ", to_file)
        if (len(to_file) < 10): # if the result is 'empty'
            return False
        else:
            return True

    def get_listing_list_full(url: str, start_pg=0, filepath="/data/listinglist/", separator="&"):
        """ cycle through all pages of listing lists """
        filepath = pathlib.Path(filepath)
        page_n = start_pg
        query = separator + "page="
        
        while (True):
            # Build the URL with proper query string
            if page_n == 0:
                # No query parameter for page 0
                page_url = url
            else:
                # Use ? separator for subsequent pages (works with test httpserver)
                # In production with PHP servers that already have params, adjust accordingly
                page_url = f"{url}{query}{page_n}"
            
            filename = filepath / f"page_{page_n}.html"
            
            # Attempt to get the page
            if (Crawler.get_listing_list_page(page_url, filename) == False):
                # Empty page, delete it and break
                if filename.exists():
                    filename.unlink()
                break
            
            page_n += 1

    def get_listing_ids_from_disk(filepath="/data/listinglist/", parser=None):
        """ retrieve all pages from disk and accumulate IDs from all pages into a single set """
        filepath = pathlib.Path(filepath)
        accumulated_ids = set()
        page_n = 0
        
        while (True):
            filename = filepath / f"page_{page_n}.html"
            
            # Check if file exists
            if not filename.exists():
                break
            
            try:
                # Read the page file
                page_data = IO.get_json(filename)
                
                # Update parser's json_list with new page data
                parser.json_list = page_data
                
                # Generate IDs from this page and merge into accumulated set
                page_ids = parser.gen_id_set()
                accumulated_ids = accumulated_ids.union(page_ids)
                
                print(f"Page {page_n}: found {len(page_ids)} IDs, total accumulated: {len(accumulated_ids)}")
                
            except Exception as e:
                warnings.warn(f"Error reading page {page_n}: {e}")
            
            page_n += 1
        
        return accumulated_ids
        
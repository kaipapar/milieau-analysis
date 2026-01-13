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
        """ download listing page html. Doesn't check for valid html, because it is parsed as txt, not html, for now"""
        filepath = pathlib.Path(filepath)
        
        if (str(filepath)[-5:] != ".html"):
            warnings.warn("method: get_listing_page: Improper filepath detected! Resorting to default")
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
            Crawler.get_listing_page(listing.url, listing.id, f"./data/listings/{listing.id}.html")
            
    def get_listing_list_page(url: str, filepath="./data/listings/") -> bool:
        """ download listing list page data as json with wget """
        if (str(filepath)[-5:] != ".json"): # if filepath doesn't end with the correct suffix
            warnings.warn("method: get_listing_list_page: Improper filepath detected! Resorting to default")
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

    def get_listing_list_full(url: str, filepath="/data/listinglist/"):
        """ cycle through all pages of listing lists """
        page_url = "&page="
        page_n = 0
        filename = lambda n : filepath+"page_"+n+".html"
        while (True):
            if (page_n == 0):
                if (Crawler.get_listing_list_page(url, filepath+filename(page_n)) == False): break
                
            elif (Crawler.get_listing_list_page(url+page_url+page_n, filepath+filename(page_n)) == False): break

            """ # same functionality as above
            if (self.is_empty(filename(page_n))):
                os.remove(filename(page_n))
                break """
            
            page_n+=1
        
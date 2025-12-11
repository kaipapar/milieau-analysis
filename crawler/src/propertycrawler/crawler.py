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
import warnings
import os

class Crawler:
    def get_listing_page(self, base_url: str, id: str, filepath="./data/listings/"):
        """ download listing page html """
        if filepath[-5:] != ".html":
            warnings.warn("method: get_listing_page: Improper filepath detected! Resorting to default")
            warnings.showwarning("Bad Filepath, using default")
            filepath = f"./listing_"+id+".html" # relative path not safe to run  anywhere
        subprocess.run(['wget', '-O', f'{filepath}', '--backups', f'{base_url+id}'])

    def get_listings(self, obj: PropertySite):
        for listing in obj.listings:
            self.get_listing_page(listing.url, listing.id, f"./data/listings/{listing.id}.html")

    def get_listing_list_page(self, url: str, filepath) -> bool:
        """ download listing list page data as json with wget """
        if filepath[-5:] != ".html":
            warnings.warn("method: get_listing_page: Improper filepath detected! Resorting to default")
            warnings.showwarning("Bad Filepath, using default")
            filepath = f"./listing_"+id+".html" # relative path not safe to run  anywhere

        #subprocess.run(['wget', '-O', f'{filepath}', '--backups', f'{url+id}']) # subprocess.run() should way for result before moving onto next line.
        
        result = subprocess.run(['wget', '-q', '-O', '-', f'{url}','|', 'tee', f'{filepath}'])
        if (result.stdout == "[]"): # if the result is empty
            return False
        else:
            return True

    def is_empty(self, filepath) -> bool:
        threshold = 100 #in bytes, it seems a empty file returned by wget is 2 bytes and a full one ~13k bytes
        if (os.path.getsize(filepath) < threshold):
            return True
        return False

    def get_listing_list_full(self, url: str, filepath="/data/listinglist/"):
        """ cycle through all pages of listing lists """
        page_url = "&page="
        page_n = 0
        filename = lambda n : filepath+"page_"+n+".html"
        while (True):
            if (page_n == 0):
                if (self.get_listing_list_page(url, filepath+filename(page_n)) == False): break
                
            elif (self.get_listing_list_page(url+page_url+page_n, filepath+filename(page_n)) == False): break

            """ # same functionality as above
            if (self.is_empty(filename(page_n))):
                os.remove(filename(page_n))
                break """
            
            page_n+=1
        
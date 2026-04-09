'''
@File: datahandler.py
@Time: 05.12.2025 17:17:45
@Author: Karri Korsu 
@Version : 1.0
@Contact : kkorsu@gmail.com
@Desc: None
'''
import json
import warnings
import io
import os
import pathlib
import pandas as pd
from propertycrawler.propertysite import PropertySite
import osmnx as ox


class IO:
    """ save and retrieve from disk """
    def get_json(path) -> list | str:
        d = []
        with open(path,'r') as file:
            d = json.load(file) #not used so the file can be inspected in stdout before throwing an error.
            """ for line in file:
                d.append(line)             
                print(line)
                json.JSONDecoder().decode(s=d) """
        return d
    
    def get_html(path) -> list:
        d = []
        with open(path,'r') as file:
             for line in file:
                  d.append(line)
        return d
    
    def get_file(path: str):
        path = pathlib.Path(path) #TODO refactoring str literal paths to Path type...
        try:
            path.exists()
        except FileNotFoundError:
            return
        with open(path) as file:
            return file
                  
    def is_empty(filepath) -> bool:
        """ returns True if file is "empty" or doesn't exist. In use with crawler methods. """
        threshold = 100 #in bytes, it seems a empty file returned by wget is 2 bytes and a full one ~13k bytes
        if (os.path.exists(filepath)):
            if (os.path.getsize(filepath) > threshold):
                return False
        return True
    
class DF:
    """ Functionalities for generating a dataset """
    def convert_dict_df(fields: list, dictionary: dict) -> pd.DataFrame:
        """ fields: tells the order and content of columns
            dictionary: the dict to be converted """
        df = pd.DataFrame(columns=fields)
        df.loc[len(df)] = dictionary
        return df
        
    def add_row(df: pd.DataFrame, row: dict):
        """ add row to existing dataframe """
        df.loc[len(df)] = row

    def add_rows(df: pd.DataFrame, listing_list):
        """ mass add rows to dataframe from listing objects.
            Works with both list and set of listing objects.
            Each listing must have an attr_dict attribute. """
        for item in listing_list:
            # Verify item has attr_dict and it's not None
            if hasattr(item, 'attr_dict') and item.attr_dict is not None:
                DF.add_row(df, item.attr_dict)
            else:
                # Log warning for listings without attr_dict
                warnings.warn(f"Listing {item.id if hasattr(item, 'id') else 'unknown'} has no attr_dict, skipping")
        return df

    def save(df: pd.DataFrame, path: str):
        """ save dataframe as csv. Creates parent directories if they don't exist. """
        path = pathlib.Path(path)
        # Create parent directories if they don't exist
        path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(path, sep=',')

class GC:
    def geocode(address: str):
        coordinates = None
        try:
            coordinates = ox.geocoder.geocode_to_gdf(address)
        except Exception as e:
            print(e)
        return coordinates

    def geocode_all(df: pd.DataFrame, addr_name: str):
        for row in df:
            row['geo'] = GC.geocode(row[addr_name])
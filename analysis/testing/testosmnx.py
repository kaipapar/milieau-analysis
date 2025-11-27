""" 
https://pythongis.org/part2/chapter-09/nb/00-retrieving-osm-data.html
 © Copyright 2020-2025, Henrikki Tenkanen, Vuokko Heikinheimo, David Whipp. 
 """
import osmnx as ox
from subprocess import check_call

place = "Kamppi, Helsinki, Finland"
aoi = ox.geocoder.geocode_to_gdf(place) # converts the query string to GeoDataFrame type variable

# In a script, save the interactive map:
m = aoi.explore()
m.save("data/kamppi_aoi.html")
#opens result with browser
check_call("firefox %s" % "data/kamppi_aoi.html", shell=True)
print("Saved map to kamppi_aoi.html")

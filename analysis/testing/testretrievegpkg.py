import geopandas as gpd
import osmnx as ox
from subprocess import check_call

# test file
file = "data/tilastointialueet.gpkg"

# import file to GeoDataFrame type
data = gpd.read_file(file)

# using data to create an interactive map

m = data.explore()
m.save("data/tilastointialueet.html")
#opens result with browser
check_call("firefox %s" % "data/tilastointialueet.html", shell=True)
print("Saved map to data/tilastointialueet.html")



import geopandas as gpd
from subprocess import check_call

name= "milieau"
dir="analysis/testing/data/"
# test file
file = f"{dir}{name}.gpkg"

# import file to GeoDataFrame type
data = gpd.read_file("analysis/testing/data/milieau_WFS.gpkg")

# using data to create an interactive map

m = data.explore()
m.save(f"{dir}milieau_WFS.html")
#opens result with browser
check_call("firefox %s" % "analysis/testing/data/milieau_WFS.html", shell=True)
print(f"Saved map to {dir}milieau_WFS.html")


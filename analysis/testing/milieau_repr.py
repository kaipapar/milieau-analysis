import geopandas as gpd
from subprocess import check_call

name= "milieau"
dir="testing/data/"
# test file
file = f"{dir} + {name}.gpkg"

# import file to GeoDataFrame type
data = gpd.read_file(file)

# using data to create an interactive map

m = data.explore()
m.save(f"{dir}+{name}.html")
#opens result with browser
check_call("firefox %s" % f"{dir}+{name}.html", shell=True)
print(f"Saved map to {dir}+{name}.html")


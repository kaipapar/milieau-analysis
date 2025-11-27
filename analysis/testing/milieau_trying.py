
import geopandas as gpd
from shapely import make_valid

gdf = gpd.read_file("milieau.json").is_closed()

# Fix invalid geometries
#gdf["geometry"] = gdf["geometry"].apply(make_valid)

# Alternatively:
#gdf["geometry"] = gdf["geometry"].buffer(0)

print("Invalid geometries after fix:", gdf[~gdf.is_valid].shape[0])

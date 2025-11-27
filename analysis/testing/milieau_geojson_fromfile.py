import geopandas as gpd
gdf = gpd.read_file("milieau.json")
print(gdf.crs)

import osmnx as ox

place = "Kamppi, Helsinki, Finland"
aoi = ox.geocoder.geocode_to_gdf(place)

# In a script, save the interactive map:
m = aoi.explore()
m.save("data/kamppi_aoi.html")
print("Saved map to kamppi_aoi.html")

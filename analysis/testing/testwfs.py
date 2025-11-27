import geopandas as gpd
import requests
import geojson
from pyproj import CRS
from owslib.wfs import WebFeatureService

# Specify the url for the backend.
# Here we are using data from Statistics Finland: https://www.stat.fi/org/avoindata/paikkatietoaineistot_en.html. (CC BY 4.0)
url = "http://geo.stat.fi/geoserver/tilastointialueet/wfs"

# Specify parameters (read data in json format).
params = dict(
    service="WFS",
    version="2.0.0",
    request="GetFeature",
    typeName="tilastointialueet:kunta4500k",
    outputFormat="json",
)

# Fetch data from WFS using requests
r = requests.get(url, params=params)

# Create GeoDataFrame from geojson and set coordinate reference system
data = gpd.GeoDataFrame.from_features(geojson.loads(r.content), crs="EPSG:3067")

print(list(data.columns.values))

# Prepare data for writing to various file formats
#data = data.drop(columns=["bbox"])

data.to_file("data/tilastointialueet.gpkg", driver="GPKG")
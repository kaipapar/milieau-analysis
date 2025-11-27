import geopandas as gpd
import requests
import geojson
from pyproj import CRS
from owslib.wfs import WebFeatureService

# Specify the url for the backend.
# Here we are using data from https://www.avoindata.fi/data/fi/dataset/turun-keskustan-miljootyypitys/resource/2129969b-8b45-4cfd-839d-a27dfeeb3918. (CC BY 4.0)
url = "https://turku.asiointi.fi/TeklaOGCWeb/WFS"

# Specify parameters (read data in json format).
params = dict(
    service="WFS",
    version="2.0.0",
    request="GetFeature",
    typeName="milieausectors:Turku",
    outputFormat="json",
)

# Fetch data from WFS using requests
r = requests.get(url, params=params)

# Create GeoDataFrame from geojson and set coordinate reference system
data = gpd.GeoDataFrame.from_features(geojson.loads(r.content), crs="EPSG:3067")

print(list(data.columns.values))

# Prepare data for writing to various file formats
#data = data.drop(columns=["bbox"])

data.to_file("data/milieau.gpkg", driver="GPKG")
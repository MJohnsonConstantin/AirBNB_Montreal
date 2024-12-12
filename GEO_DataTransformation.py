import geopandas as gpd
import pandas as pd
from shapely.geometry import shape

GEO_Files = [
    "Raw_Data/neighbourhoods_GEO_12-2023.geojson",
    "Raw_Data/neighbourhoods_GEO_06-2024.geojson",
    "Raw_Data/neighbourhoods_GEO_03-2024.geojson",
    "Raw_Data/neighbourhoods_GEO_09-2024.geojson"
]

#Reading, importing and concatenating the csv files into a single dataframe
dataframes_GEO = [gpd.read_file(file) for file in GEO_Files]
GEO_data = gpd.GeoDataFrame(pd.concat(dataframes_GEO,  ignore_index=True))

#DATA VALIDATION 
print(GEO_data.info())
print(GEO_data["neighbourhood_group"])

#DELETING neigh_group columns
GEO_data = GEO_data.drop(columns="neighbourhood_group")

# Check the total number of duplicates
duplicate_count = GEO_data.duplicated().sum()
print(f"Total duplicate rows: {duplicate_count}")

# Display the duplicate rows
duplicates = GEO_data[GEO_data.duplicated()]
print("Duplicate rows:")
print(duplicates)

# Keep only the first occurrence
GEO_data = GEO_data.drop_duplicates(keep="first")

# Verify the result
print(f"Rows after keeping the first occurrence of duplicates: {len(GEO_data)}")

#LAST DATA VALIDATION 
print(GEO_data.isna().sum())

#Transforming polygon data for POWER BI 
# Step 1: Load Data
GEO_data['geometry'] = GEO_data['geometry'].apply(shape)  # Parse MULTIPOLYGON geometries

# Step 2: Create GeoDataFrame with CRS EPSG:4326
gdf = gpd.GeoDataFrame(GEO_data, geometry='geometry', crs="EPSG:4326")

# Step 3: Reproject to a Projected CRS for Accurate Centroid Calculation
gdf = gdf.to_crs(epsg=32188)  # Use a projected CRS (e.g., EPSG:32188)
gdf['projected_centroid'] = gdf.geometry.centroid  # Calculate centroids in projected CRS

# Step 4: Reproject Back to Geographic CRS (EPSG:4326)
gdf = gdf.to_crs(epsg=4326)  # Reproject to WGS84

# Step 5: Recalculate Centroid in EPSG:4326 Directly from the Geometry
gdf['centroid'] = gdf.geometry.centroid  # Recalculate centroids in EPSG:4326
gdf['latitude'] = gdf['centroid'].apply(lambda point: point.y)  # Extract latitude
gdf['longitude'] = gdf['centroid'].apply(lambda point: point.x)  # Extract longitude

# Step 6: Save to CSV
gdf[['neighbourhood', 'latitude', 'longitude']].to_csv("GEO_data.csv", index=False)

# Print Results to Verify
print(gdf[['neighbourhood', 'latitude', 'longitude']].head())


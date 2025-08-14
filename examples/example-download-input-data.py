from data_downloader import DataDownloader

import os
import zipfile
import csv
import time
from urllib.parse import urlparse


# Create an instance of the DataDownloader class
downloader = DataDownloader(download_path="data/in-3p")

# --------------------------------------------------------
# Function to unzip a file to a specified directory
def unzip_file(zip_file_path, extract_to):
    print(f"Unzipping {zip_file_path} to {extract_to}...")
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    print(f"Unzipped {zip_file_path} successfully!")
    
# --------------------------------------------------------
# Function to replace the .prj file with WKT2 EPSG:4283
def replace_prj_with_epsg_4283(shapefile_path):
    prj_file = os.path.splitext(shapefile_path)[0] + ".prj"
    print(f"Replacing .prj file at {prj_file} with EPSG:4283 WKT2...")
    # Generate WKT2 string for EPSG:4283 using pyproj
    # from pyproj import CRS
    # wkt_content = CRS.from_epsg(4283).to_wkt("WKT2_2019")
    # with open(prj_file, "w") as f:
    #     f.write(wkt_content)
    print(".prj file successfully replaced! (placeholder)")
    
    
print("Downloading source data files. This will take a while ...")
    
# --------------------------------------------------------
# Australian Coastline 50K 2024 (NESP MaC 3.17, AIMS)
# https://eatlas.org.au/geonetwork/srv/eng/catalog.search#/metadata/c5438e91-20bf-4253-a006-9e9600981c5f
# Hammerton, M., & Lawrey, E. (2024). Australian Coastline 50K 2024 (NESP MaC 3.17, AIMS) (2nd Ed.) [Data set]. eAtlas. https://doi.org/10.26274/qfy8-hj59
# Here we download parts of the full datasets and place them into subfolders. We flatten because the original zip contains subfolder
# `Split` which we don't need because we are putting it in the subfolder `Split`. Without flattening, the files would be in 
# `Split/Split/` which is not what we want. 
# If we didn't use subfolder_name, with no flattening then the files would be in `AU_AIMS_Coastline_50k_2024/Split/` which is fine,
# but when we want to add the Simp version the script would skip the download because it would see that the AU_AIMS_Coastline_50k_2024 
# folder already exists.
# The skip checking is done on the dataset name and the subfolder_name.
direct_download_url = 'https://nextcloud.eatlas.org.au/s/DcGmpS3F5KZjgAG/download?path=%2FV1-1%2F&files=Split'
downloader.download_and_unzip(direct_download_url, 'AU_AIMS_Coastline_50k_2024', subfolder_name='Split', flatten_directory=True)

# Use this version for overview maps
direct_download_url = 'https://nextcloud.eatlas.org.au/s/DcGmpS3F5KZjgAG/download?path=%2FV1-1%2F&files=Simp'
downloader.download_and_unzip(direct_download_url, 'AU_AIMS_Coastline_50k_2024', subfolder_name='Simp', flatten_directory=True)

# --------------------------------------------------------
# Natural Earth. (2025). Natural Earth 1:10m Physical Vectors - Land [Shapefile]. https://www.naturalearthdata.com/downloads/10m-physical-vectors/
direct_download_url = 'https://naciscdn.org/naturalearth/10m/physical/ne_10m_land.zip'
downloader.download_and_unzip(direct_download_url, 'ne_10m_land')

# --------------------------------------------------------
#Lawrey, E. P., Stewart M. (2016) Complete Great Barrier Reef (GBR) Reef and Island Feature boundaries including Torres Strait (NESP TWQ 3.13, AIMS, TSRA, GBRMPA) [Dataset]. Australian Institute of Marine Science (AIMS), Torres Strait Regional Authority (TSRA), Great Barrier Reef Marine Park Authority [producer]. eAtlas Repository [distributor]. https://eatlas.org.au/data/uuid/d2396b2c-68d4-4f4b-aab0-52f7bc4a81f5
direct_download_url = 'https://nextcloud.eatlas.org.au/s/xQ8neGxxCbgWGSd/download/TS_AIMS_NESP_Torres_Strait_Features_V1b_with_GBR_Features.zip'
downloader.download_and_unzip(direct_download_url, 'GBR_AIMS_Complete-GBR-feat_V1b')

# Replace the .prj file for the GBR shapefile because it is using an older WKT format
# that fails to load correctly in stages 3.
gbr_shapefile = os.path.join(downloader.download_path, 'GBR_AIMS_Complete-GBR-feat_V1b', 'TS_AIMS_NESP_Torres_Strait_Features_V1b_with_GBR_Features.shp')
replace_prj_with_epsg_4283(gbr_shapefile)

# --------------------------------------------------------
# Lawrey, E. (2024). Coral Sea Oceanic Vegetation (NESP MaC 2.3, AIMS) [Data set]. eAtlas. https://doi.org/10.26274/709g-aq12
direct_download_url = 'https://nextcloud.eatlas.org.au/s/9kqgb45JEwFKKJM/download'
downloader.download_and_unzip(direct_download_url, 'CS_NESP-MaC-2-3_AIMS_Oceanic-veg', flatten_directory=True)


# --------------------------------------------------------
# McNeil, M.A., Webster, J.M., Beaman, R.J. et al. New constraints on the spatial distribution and morphology of the Halimeda bioherms of the Great Barrier Reef, Australia. Coral Reefs 35, 1343–1355 (2016). https://doi.org/10.1007/s00338-016-1492-2
# https://static-content.springer.com/esm/art%3A10.1007%2Fs00338-016-1492-2/MediaObjects/338_2016_1492_MOESM1_ESM.zip
# Also available from https://geoserver.imas.utas.edu.au/geoserver/seamap/wfs?version=1.0.0&request=GetFeature&typeName=SeamapAus_QLD_Halimeda_bioherms_2016&outputFormat=SHAPE-ZIP
# https://metadata.imas.utas.edu.au/geonetwork/srv/eng/catalog.search#/metadata/b8475bea-e24e-4374-8090-ef06514b951d
direct_download_url = 'https://static-content.springer.com/esm/art%3A10.1007%2Fs00338-016-1492-2/MediaObjects/338_2016_1492_MOESM1_ESM.zip'
downloader.download_and_unzip(direct_download_url, 'GBR_USYD_Halimeda-bioherms_2016', flatten_directory=True)

# --------------------------------------------------------
# The rough reef mask corresponds to the water estimate
# masking created for the creation of this dataset
# Switch to a different download path
# By convention we use `data/in` for input data that is new data associated with the datasets being created
# and we use `data/in-3p` for input data that is used in the 3rd party datasets.
downloader.download_path = "data/in"

direct_download_url = 'https://nextcloud.eatlas.org.au/s/iMrFB9WP9EpLPC2/download?path=%2FV1%2Fin-data%2FAU_Rough-reef-shallow-mask'
downloader.download_and_unzip(direct_download_url, 'AU_Rough-reef-shallow-mask', flatten_directory=True)

direct_download_url = 'https://nextcloud.eatlas.org.au/s/iMrFB9WP9EpLPC2/download?path=%2FV1%2Fin-data%2FAU_Cleanup-remove-mask'
downloader.download_and_unzip(direct_download_url, 'AU_Cleanup-remove-mask', flatten_directory=True)

# --------------------------------------------------------
# Reef features on the Australian continental shelf derived and aggregated from 
# Australian Hydrographic Service's (AHS) seabed area features (sbdare_a) from the 1 degree S57 file series [for NESP D3]
# https://catalogue.aodn.org.au/geonetwork/srv/eng/catalog.search#/metadata/2e53d926-5d97-4997-b192-dc7dec66943d
direct_download_url = 'https://data.imas.utas.edu.au/attachments/2e53d926-5d97-4997-b192-dc7dec66943d/sbdare_a_reefs-only.zip'
downloader.download_and_unzip(direct_download_url, 'AU_NESP-D3_AHO_Reefs')


# --------------------------------------------------------
# Australian land and coastline (including Lord Howe Island) at lowest astronomical tide (LAT) datum [for NESP D3]
# https://catalogue.aodn.org.au/geonetwork/srv/eng/catalog.search#/metadata/2e53d926-5d97-4997-b192-dc7dec66943d
direct_download_url = 'https://data.imas.utas.edu.au/attachments/358afb92-4977-4f9f-9c74-e66ad7a6c65a/aho_land_lat.zip'
downloader.download_and_unzip(direct_download_url, 'AU_NESP-D3_AHO_Land')


# --------------------------------------------------------
# Hart-Davis Michael, Piccioni Gaia, Dettmering Denise, Schwatke Christian, Passaro Marcello, Seitz Florian (2021). 
# EOT20 - A global Empirical Ocean Tide model from multi-mission satellite altimetry. SEANOE. https://doi.org/10.17882/79489
#
# Hart-Davis Michael G., Piccioni Gaia, Dettmering Denise, Schwatke Christian, Passaro Marcello, Seitz Florian (2021). 
# EOT20: a global ocean tide model from multi-mission satellite altimetry. Earth System Science Data, 13 (8), 3869-3884.
# https://doi.org/10.5194/essd-13-3869-2021


# NOTE: The EOT20 download includes two zip files inside the downloaded zipfile, we only use ocean_tides.zip.
direct_download_url = 'https://www.seanoe.org/data/00683/79489/data/85762.zip'
eot20_folder = 'World_EOT20_2021'
downloader.download_and_unzip(direct_download_url, eot20_folder)

# Prepare paths for load_tides and ocean_tides zip files
base_path = os.path.join(downloader.download_path, eot20_folder)
load_tides_zip = os.path.join(base_path, "load_tides.zip")
ocean_tides_zip = os.path.join(base_path, "ocean_tides.zip")

# Unzip ocean_tides.zip
ocean_tides_folder = os.path.join(base_path, "ocean_tides")
if os.path.exists(ocean_tides_folder):
    print(f"{ocean_tides_folder} found. Skipping...")
else:
    unzip_file(ocean_tides_zip, base_path)

# Remove load_tides.zip as we don't use it in the simulation. Do this to save space.
if os.path.exists(load_tides_zip):
    print(f"Removing {load_tides_zip}...")
    os.remove(load_tides_zip)
    print(f"{load_tides_zip} removed successfully!")

print("All files are downloaded and prepared.")

# --------------------------------------------------------
# Tide Gauge Monthly Stats Data
# Source: http://www.bom.gov.au/oceanography/projects/abslmp/data/monthly.shtml
# http://www.bom.gov.au/oceanography/projects/ntc/monthly/
# In this example we are downloading a bunch of files specified from a CSV file.

# Path to the CSV file containing tide gauge data
tide_gauges_csv = "data/BOM_tide-gauges.csv"

# Define the destination folder for the tide gauge monthly stats
tide_stats_folder = os.path.join(downloader.download_path, "AU_BOM_Monthly-tide-stats")
os.makedirs(tide_stats_folder, exist_ok=True)

# Open the CSV and iterate through each tide gauge entry
with open(tide_gauges_csv, newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        monthly_stats_url = row["MonthlyStatsURL"]
        # Generate a filename using the tide gauge ID.
        #file_name = f"{row['ID']}.txt"
        # Extract the filename from the URL and replace its extension with .txt
        parsed_url = urlparse(monthly_stats_url)
        original_filename = os.path.basename(parsed_url.path)
        file_name = os.path.splitext(original_filename)[0] + '.txt'

        destination_file = os.path.join(tide_stats_folder, file_name)

        # Check if the file already exists
        if os.path.exists(destination_file):
            print(f"{destination_file} already exists. Skipping download...")
            continue
        
        print(f"Downloading monthly tide stats for {row['StationName']} from {monthly_stats_url}...")
        downloader.download(monthly_stats_url, destination_file)

        # Pause for 2 seconds between downloads to avoid overloading the server.
        time.sleep(1)
      
# --------------------------------------------------------
# Lawrey, E., & Hammerton, M. (2022). Coral Sea features satellite imagery and raw depth contours (Sentinel 2 and Landsat 8) 2015 – 2021 (AIMS) [Data set]. eAtlas. https://doi.org/10.26274/NH77-ZW79

# We set the subfolder_name because we are downloading multiple folders into the same parent folder. This allows the script
# to check if the sub part of the dataset has been downloaded already. Without this the TrueColour download is skipped because
# the Coral-Sea-Features_Img folder already exists.
dataset = 'Coral-Sea-Features_Img'

layer = 'S2_R1_DeepFalse'
direct_download_url = f'https://nextcloud.eatlas.org.au/s/NjbyWRxPoBDDzWg/download?path=%2Flossless%2FCoral-Sea&files={layer}'
downloader.download_and_unzip(direct_download_url, dataset, subfolder_name = layer, flatten_directory = True)

layer = 'S2_R2_DeepFalse'
direct_download_url = f'https://nextcloud.eatlas.org.au/s/NjbyWRxPoBDDzWg/download?path=%2Flossless%2FCoral-Sea&files={layer}'
downloader.download_and_unzip(direct_download_url, dataset, subfolder_name = layer, flatten_directory = True)

layer = 'S2_R1_TrueColour'
direct_download_url = f'https://nextcloud.eatlas.org.au/s/NjbyWRxPoBDDzWg/download?path=%2Flossless%2FCoral-Sea&files={layer}'
downloader.download_and_unzip(direct_download_url, dataset, subfolder_name = layer, flatten_directory = True)

# Raw depth contours
direct_download_url = f'https://nextcloud.eatlas.org.au/s/NjbyWRxPoBDDzWg/download?path=%2Fpoly&files=Coral-Sea'
downloader.download_and_unzip(direct_download_url, dataset, subfolder_name = 'Raw-depth')

# --------------------------------------------------------
# ICSM (2018) ICSM ANZLIC Committee on Surveying and Mapping Data Product Specification for Composite Gazetteer of Australia, The Intergovernmental Committee on Surveying and Mapping. Accessed from https://placenames.fsdf.org.au/ on 23 Jan 2025
# https://s3.ap-southeast-2.amazonaws.com/fsdf.placenames/DPS/Composite+Gazetteer+DPS.pdf
direct_download_url = 'https://d1tuzeg87mu4oi.cloudfront.net/PlaceNames.gpkg'
downloader.download(direct_download_url, 'AU_ICSM_Gazetteer_2018')


# --------------------------------------------------------
# Geoscience Australia (2021). Kenn and Chesterfield Plateaux bathymetry survey (FK210206/GA4869) [Dataset]. Geoscience Australia, Canberra. https://doi.org/10.26186/145381
# https://dx.doi.org/10.26186/145381
direct_download_url = 'https://files.ausseabed.gov.au/survey/Kenn%20and%20Chesterfield%20Plateaux%20Bathymetry%202021%2064m.zip'
downloader.download_and_unzip(direct_download_url, 'CS_GA_Kenn-Chesterfield-Bathy')

# --------------------------------------------------------
# Geoscience Australia (2020). Northern Depths of the Great Barrier Reef bathymetry survey (FK200930/GA4866) [Dataset]. Geoscience Australia, Canberra. http://pid.geoscience.gov.au/dataset/ga/144545
direct_download_url = 'https://files.ausseabed.gov.au/survey/Northern%20Great%20Barrier%20Reef%20Bathymetry%202020%2064m.zip'
downloader.download_and_unzip(direct_download_url, 'CS_GA_North-GBR-Bathy')

# --------------------------------------------------------
# Spinoccia, M., Brooke, B., Nichol, S., & Beaman, R. (2020). Seamounts, Canyons and Reefs of the Coral Sea bathymetry survey (FK200802/GA0365) [Dataset]. Commonwealth of Australia (Geoscience Australia). https://doi.org/10.26186/144385
direct_download_url = 'https://files.ausseabed.gov.au/survey/Coral%20Sea%20Canyons%20and%20Reef%20Bathymetry%202020%2016m%20-%2064m.zip'
downloader.download_and_unzip(direct_download_url, 'CS_GA_Coral-Sea-Canyons')

# --------------------------------------------------------
# Beaman, R., Duncan, P., Smith, D., Rais, K., Siwabessy, P.J.W., Spinoccia, M. (2020). Visioning the Coral Sea Marine Park bathymetry survey (FK200429/GA4861). Geoscience Australia, Canberra. https://dx.doi.org/10.26186/140048
direct_download_url = 'https://files.ausseabed.gov.au/survey/Visioning%20the%20Coral%20Sea%20Bathymetry%202020%2016m%20-%2064m.zip'
downloader.download_and_unzip(direct_download_url, 'CS_GA_Visioning-Coral-Sea-Bathy')

# --------------------------------------------------------
# Beaman, R. (2020). High-resolution depth model for the Great Barrier Reef and Coral Sea - 100 m [Dataset]. Geoscience Australia. http://doi.org/10.26186/5e2f8bb629d07
direct_download_url = 'https://files.ausseabed.gov.au/survey/Great%20Barrier%20Reef%20Bathymetry%202020%20100m.zip'
downloader.download_and_unzip(direct_download_url, 'CS_GA_GBR100-2020-Bathy')

# --------------------------------------------------------
# Beaman, R. (2017). High-resolution depth model for the Great Barrier Reef - 30 m [Dataset]. Geoscience Australia. http://dx.doi.org/10.4225/25/5a207b36022d2
direct_download_url = 'https://files.ausseabed.gov.au/survey/Great%20Barrier%20Reef%20Bathymetry%202020%2030m.zip'
downloader.download_and_unzip(direct_download_url, 'CS_GA_GBR30-2020-Bathy')

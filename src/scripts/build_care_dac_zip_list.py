
"""build_care_dac_zip_list.py
Creates CARE + DAC enriched ZIP list for California.
Run locally after placing High_CARE_ZIPs_CA.csv at repo root.
"""
import pathlib, requests, zipfile, io, pandas as pd, geopandas as gpd

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
DATA_DIR = REPO_ROOT / "data"
ZCTA_DIR = DATA_DIR / "zcta"
DAC_DIR = DATA_DIR / "dac"

ZCTA_URL = "https://www2.census.gov/geo/tiger/TIGER2023/ZCTA5/tl_2023_us_zcta520.zip"
DAC_URL = "https://d2atf2g1dvl9s2.cloudfront.net/sites/default/files/CES4shp.zip"

def download_and_extract(url, dest_dir):
    dest_dir.mkdir(parents=True, exist_ok=True)
    fname = dest_dir / "tmp.zip"
    print(f"Downloading {url} ...")
    r = requests.get(url, timeout=60)
    r.raise_for_status()
    fname.write_bytes(r.content)
    with zipfile.ZipFile(fname) as z:
        z.extractall(dest_dir)
    fname.unlink()

if not any(ZCTA_DIR.glob("*.shp")):
    download_and_extract(ZCTA_URL, ZCTA_DIR)
if not any(DAC_DIR.glob("*.shp")):
    download_and_extract(DAC_URL, DAC_DIR)

zcta_path = next(ZCTA_DIR.glob("*.shp"))
dac_path = next(DAC_DIR.glob("*.shp"))

zcta = gpd.read_file(zcta_path)[["ZCTA5CE20", "geometry"]]
zcta = zcta.rename(columns={"ZCTA5CE20": "ZIP"})
zcta = zcta[zcta["ZIP"].str.startswith("9")]

dac = gpd.read_file(dac_path)[["SB535", "geometry"]]
dac = dac[dac["SB535"] == 1]

care_csv = REPO_ROOT / "High_CARE_ZIPs_CA.csv"
if not care_csv.exists():
    raise FileNotFoundError("Place High_CARE_ZIPs_CA.csv at repo root before running.")
care_df = pd.read_csv(care_csv, dtype={"ZIP": str})

care_geo = gpd.GeoDataFrame(care_df.merge(zcta, on="ZIP", how="left"),
                            geometry="geometry", crs=zcta.crs)
care_geo["DAC_Flag"] = care_geo.sjoin(dac, how="left", predicate="intersects")["SB535"].notna()
care_geo["DAC_Flag"] = care_geo["DAC_Flag"].map({True: "Yes", False: "No"})

# county + pop crosswalk
crosswalk = pd.read_csv("https://www2.census.gov/geo/docs/maps-data/data/rel/zcta_county_rel_10.txt",
                        dtype={"ZCTA5": str, "COUNTY": str})
care_geo = care_geo.merge(crosswalk[["ZCTA5", "COUNTY"]].rename(columns={"ZCTA5": "ZIP"}),
                          on="ZIP", how="left")

county_names = pd.read_csv("https://raw.githubusercontent.com/kjhealy/fips-codes/master/state_and_county_fips_master.csv",
                           dtype=str)[["fips","name"]].rename(columns={"fips":"COUNTY","name":"County_Name"})
care_geo = care_geo.merge(county_names, on="COUNTY", how="left")

out_csv = REPO_ROOT / "CARE_DAC_ZIPs_Enriched.csv"
care_geo.drop(columns="geometry").to_csv(out_csv, index=False)
print("Done. File written:", out_csv)

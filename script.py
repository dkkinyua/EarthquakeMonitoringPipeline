import os
import requests
import pandas as pd
from dotenv import load_dotenv
from datetime import date, timedelta
from sqlalchemy import create_engine

load_dotenv()

def extract_data():
    earthquake_data = []
    BASE_URL = "https://earthquake.usgs.gov/fdsnws/event/1/query"
    today = date.today()
    start_date = today - timedelta(days=1)
    params = {
        "format": "geojson",
        "starttime": start_date,
        "endtime": today
    }

    response = requests.get(BASE_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        for feature in data["features"]:
            props = feature["properties"]
            coords = feature["geometry"]["coordinates"]

            quake = {
                "id": feature["id"],
                "magnitude": props["mag"],
                "mag_type": props.get("magType"),
                "place": props.get("place"),
                "time": props.get("time"),
                "updated": props.get("updated"),
                "status": props.get("status"),
                "tsunami": props.get("tsunami"),
                "event_type": props.get("type"),
                "significance": props.get("sig"),
                "net": props.get("net"),
                "code": props.get("code"),
                "ids": props.get("ids"),
                "url": props.get("url"),
                "alert": props.get("alert"),       
                "longitude": coords[0],
                "latitude": coords[1],
                "depth": coords[2]
            }
            earthquake_data.append(quake)

        return earthquake_data
    else:
        print(f"Error extracting data from USGS URL: {response.status_code}, {response.text}")

def transform_load(data):
    df = pd.DataFrame(data)
    df["time"] = pd.to_datetime(df["time"] / 1000, unit='s')
    df["updated"] = pd.to_datetime(df["updated"] / 1000, unit='s')
    ssl_args = {
        'ssl': {
            "ca": "/home/deecodes/EarthquakeMonitoringPipeline/.certs/ca.pem"
        }
    }
    engine = create_engine(os.getenv("MYSQL_URI"), connect_args=ssl_args)
    try:
        df.to_sql('earthquake_data', con=engine, schema='earthquake', index=False, if_exists='append')
        print("Data loaded into MySQL database successfully!")
    except Exception as e:
        print(f"Error loading data into MySQL database: {e}")

data = extract_data()
transform_load(data)
    


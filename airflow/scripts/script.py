import os
import smtplib
import requests
import pandas as pd
from dotenv import load_dotenv
from datetime import date, timedelta
from email.mime.text import MIMEText
from sqlalchemy import create_engine

load_dotenv()

# send emails about earthquakes of a significant magnitude level
def send_email(data):
    body = f"""
            There's an earthquake occured at {data["place"]}.
            Magnitude intensity: {data["magnitude"]}
            Alert type: {data["alert"]}
            Latitude: {data["latitude"]}
            Longitude: {data["longitude"]}

            For more information on this earthquake visit: {data["url"]}
            Important information.
            If the alert is:
                a. Green: 0 estimated fatalities, < $ 1M losses. No need for panic
                b. Yellow: 1 - 99 estimated fatalities, $ 1M - $ 100M estimated losses
                c. Orange: 100 - 999 estimated fatalities, $ 100M - $ 1b estimated losses
                d. Red: 1000+ estimated fatalities, > $ 1b estimated losses.
                e. None/Null: No need for panic.
            Stay safe.
            """
    subject = "Earthquake notification."
    sender = os.getenv("SENDER")
    receipients = [os.getenv('RECEIPIENT')]
    pwd = os.getenv("PASSWORD")

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = receipients[0]

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
        try:
            smtp_server.login(sender, pwd)
            smtp_server.sendmail(sender, receipients, msg.as_string())
            print(f"Email sent successfully for {data['place']}!")
        except Exception as e:
            print(f"Sending email to receipient error: {e}")

def etl_process():
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
            
            # send email if mag >= 4.5
            if quake["magnitude"] >= 4.5:
                send_email(quake)

        return earthquake_data
    else:
        print(f"Error extracting data from USGS URL: {response.status_code}, {response.text}")

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
        

    


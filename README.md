# EarthquakeMonitoringPipeline
This project contains an end-to-end data pipeline that extracts data from the USGS Earthquake API, loads into a MySQL database, connects it to a Kafka topic using a MySQL CDC Connector, sinks the data into a PostgreSQL database using a Postgres Sink Connector fully hosted on Confluent and visualizes real-time data on a Grafana Cloud dashboard. The script is run automatically on an hourly basis by Apache Airflow.

## Project Architecture.

Below is the project workflow used in this project.

![Project Workflow](https://res.cloudinary.com/depbmpoam/image/upload/v1752054404/Screenshot_2025-07-09_124443_zwk6ef.png)

## Project Features

- Real-time data ingestion from [USGS Earthquake Feed](https://earthquake.usgs.gov/earthquakes/feed/v1.0/geojson.php)
- CDC (Change Data Capture) using **Debezium** MySQL CDC Connector
- Kafka streaming with **Confluent Cloud**
- Sink to PostgreSQL using Postgres Sink Connector
- Visualization in Grafana to derive insights on:
    - Quakes Per Minute
    - Quakes Per Minute with Alerts
    - Top 5 Quake Hotspot regions
    - Real-time World map to show earthquake locations

## Project Setup

### 1. Clone the project
Open your terminal and run the following command:

```bash
git clone https://github.com/dkkinyua/EarthquakeMonitoringPipeline
```

### 2. Activate the virtual environment and install the required dependencies
To install and activate a virtual environment, run the following commands in your terminal:

```bash
cd EarthquakeMonitoringPipeline
python3 -m venv yourvenv
source yourvenv/bin/activate # Linux/MacOS
yourvenv\Scripts\activate # Windows
```

After activating your virtual environment, install this project's dependencies:

```bash
pip install -r requirements.txt
```

### 3. MySQL configuration for Debezium connection

For a successful connection, head over to the MySQL configuration file to edit some settings to allow replication and logging in our database.

Run the following command to edit the file:

```bash
sudo nano /etc/mysql/mysql.conf.d/mysql.cnf
```

Then edit/add the following settings:

```ini
server-id               = 12345
log_bin                 = /var/log/mysql/mysql-bin.log
binlog_expire_logs_seconds      = 2592000
binlog_format    = ROW
max_binlog_size   = 100M
expire_logs_days = 7
```
### 4. MySQL Debezium CDC Connector Configuration

Below are some settings, instructions, and snapshots on how to set your MySQL Debezium Connector to connect our MySQL database to a Kafka topic.

- a. Head over to Confluent Cloud, sign up for an account / sign in to your existing account.
- b. Create a new environment, cluster, and go to **Connectors** on your left-hand side. Search for **MySQLCDCConnectorv2 for Debezium** and start the connector setup.

> NOTE: Please set your output value to `JSON_SR` format because our Postgres Sink connector only allows Avro, `JSON_SR`, and Protobuf input formats. `JSON_SR` is JSON Schema Registry format.

### 5. Postgres Sink Connector Configuration

- a. Go to **Connectors** and search for **Postgres Sink** connector and start the connector setup.

> NOTE: Set input value format to `JSON_SR` to match the output value format in the MySQL connector to avoid errors. Also, by default, the data is sent to a table equal to the topic + schema + table name from the MySQL connector topics. Head over to **Advanced Settings** and select *Table name format* and set it to schema + table name as set in your Postgres database to load data in the correct database. The data is stored in the `after` section in our JSON input (Check Topic for more details), use a Transformation in the **Transforms** settings section to only select data from the `after` section.

### 6. Apache Airflow Configuration
The Airflow version used in this project is `apache-airflow==2.10.5`. You can install this package via `requirements.txt`, or you can download it with the constraints file by running the following command:
```bash
pip install apache-airflow==2.10.5 --constraint https://raw.githubusercontent.com/apache/airflow/constraints-2.10.5/constraints-3.10.txt
```

> NOTE: Airflow cannot run on Windows. Use Windows Subsystem for Linux (WSL) or use a Docker container to use Airflow on a Windows machine

To set up `AIRFLOW_HOME` to hold our configuration files, run the following command:
```bash
export AIRFLOW_HOME='path/to/EarthquakeMonitoringPipeline/airflow'
```
Then run the following command to initialize Airflow in our project

```bash
airflow db init
```
This will create `airflow.cfg`, `airflow.db`, and other files inside the `airflow` directory.

Go to the airflow directory, and edit the `airflow.db` file to change the default timezone, change email settings to allow Airflow to send emails via SMTP and not to load examples into the Airflow UI when accessing the webserver
```bash
cd airflow
nano airflow.cfg
```
Change the following settings:
```ini
load_examples = False # default True
smtp_host = smtp.gmail.com
smtp_ssl = True
smtp_user = your_email@gmail.com
smtp_password = your_app_password
smtp_mail_from = your_email@gmail.com
```
Create a new Admin to access the web server and Airflow UI, and migrate changes to the database.

```bash
airflow users create --firstname first --lastname last --email email@email.com --role Admin --password pass
airflow db migrate
```

Start your web server and scheduler

```bash
airflow webserver & airflow scheduler
```

You can access the Airflow UI at localhost:8080
![Airflow UI](https://res.cloudinary.com/depbmpoam/image/upload/v1752259858/Screenshot_2025-07-11_203233_ilpwny.png)

## Grafana dashboards
The insights derived from this data is:
- Quakes Per Minute
- Quakes Per Minute with Alerts
- Top 5 Quake Hotspot regions
- Real tie World map to show earthquake locations

Below are snapshots from the dashboard. If you would want to access the dashboard, click [here](https://deecodes.grafana.net/goto/GFkNW_sNg?orgId=1) to access the dashboard.

![Dash 1](https://res.cloudinary.com/depbmpoam/image/upload/v1752054532/Screenshot_2025-07-09_124803_n8gtsf.png)

![Dash 2](https://res.cloudinary.com/depbmpoam/image/upload/v1752054531/Screenshot_2025-07-09_124820_eokzg4.png)

## Conclusion

Do you have any additions or changes? Pull Requests are welcome!




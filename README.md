# usom-ioc-fetcher

This project is a Python script designed to retrieve and filter Indicators of Compromise (IoC) data provided by Turkey's National Cyber Incident Response Center (USOM). It is intended to be periodically and automatically executed using Apache Airflow.

# Features:

Pulls IoC data from USOM page by page and saves it as a local JSON file.
Automatically waits and tries again when the API limits.
Saves IoC data after the specified date in a separate file.
Runs periodically using Airflow.

# Technologies Used:

Python 3.x
Apache Airflow
requests library

# Installation:

First, clone the project repository on GitHub to your computer.

git clone https://github.com/canakkaya-ceng/usom-ioc-fetcher.git

cd usom-ioc-fetcher

Install the necessary Python libraries:

pip install requests apache-airflow

Copy the script file to Airflow's DAG folder. Usually this directory is ~/airflow/dags/:

cp usom_ioc_fetcher.py ~/airflow/dags/

Go to the Airflow web interface and activate the DAG.DAG is set to run daily. If you want to change the run period, you can update the 'schedule' parameter in the code.

Generated Files: When the script is run, two JSON files will be created on the desktop:

For all IoC data: output_ioc.json
For date filtered IoC data: filtered_output_ioc.json
You can edit the relevant sections in the script to change these file paths.

Lisans: This project is licensed under the MIT license. You can use, modify and distribute it as you wish. You can check the LICENSE file for details.


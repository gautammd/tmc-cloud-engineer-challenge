import json
import csv
import boto3
from datetime import datetime
import pandas as pd
import time
from io import StringIO
import os
import sqlalchemy

def process_upload(event, context):
    bucket = event['Records'][0]['s3']['bucket']['name']
    uploadedfile = event['Records'][0]['s3']['object']['key'] if 'pace-data' in event['Records'][0]['s3']['object']['key'] else None
    if uploadedfile is None:
        return
    
    # Read the file from S3
    s3 = boto3.client('s3')
    print('Reading file from S3')
    s3_object = s3.get_object(Bucket=bucket, Key=uploadedfile)
    s3_data = s3_object['Body'].read().decode('utf-8')
    print('File read from S3')

    # Parse the file
    print('Parsing file')
    csv_data = csv.reader(s3_data.splitlines(), delimiter=',')
    print('File parsed')

    # Upload csv file to s3
    print('Uploading file to S3')
    s3.put_object(Bucket=bucket, Key=f'data/input/raw/pace-data-{int(time.time())}.csv', Body=s3_data)
    print('File uploaded to S3')


def transform_data(event, context):
    bucket = event['Records'][0]['s3']['bucket']['name']
    uploadedfile = event['Records'][0]['s3']['object']['key'] if 'pace-data' in event['Records'][0]['s3']['object']['key'] else None
    if uploadedfile is None:
        return
    
    # Read the file from S3
    s3 = boto3.client('s3')
    print('Reading file from S3')
    print(uploadedfile)
    s3_object = s3.get_object(Bucket=bucket, Key=uploadedfile)
    s3_data = s3_object['Body'].read().decode('utf-8')
    print('File read from S3')

    # read csv file using pandas
    print('Reading csv file using pandas')
    df = pd.read_csv(StringIO(s3_data), sep=',')
    print('Csv file read using pandas')

    # Transform the data
    print('Transforming data')
    # normalize MovementDateTime to iso 8601 format
    df['MovementDateTime'] = pd.to_datetime(df['MovementDateTime'], format='%Y-%m-%d %H:%M:%S')
    df['MovementDateTime'] = df['MovementDateTime'].dt.strftime('%Y-%m-%d %H:%M:%S')

    # get average speed from column CallSign
    df['AverageSpeed'] = df.groupby('CallSign')['Speed'].transform('mean')

    # replace CallSign with average speed where CallSign is zero or Null
    df['CallSign'] = df['CallSign'].fillna(df['AverageSpeed'])

    # add a column BeamRatio to the dataframe calculated from Beam divided by Length
    df['BeamRatio'] = df['Beam'] / df['Length']

    # write the transformed data to a csv file
    print('Writing transformed data to csv file')
    csv_data = df.to_csv(index=False)
    s3.put_object(Bucket=bucket, Key=f'data/output/raw/pace-data-{int(time.time())}.csv', Body=csv_data)
    print('Transformed data written to csv file')

    #connect to postgres database
    print('Connecting to postgres database')
    db_url = f"postgresql://{os.environ.get('user')}:{os.environ.get('pass')}@{os.environ.get('host')}/{os.environ.get('dbname')}"
    engine = sqlalchemy.create_engine(db_url)
    print('Connected to postgres database')

    # create a new table in the database with the transformed data
    print('Creating new table in postgres database')
    table_name = f'pace_data_{int(time.time())}'
    print(f"Table Name: {table_name}")
    df.to_sql(table_name, engine)
    print('New table created in postgres database')

def get_data(event, context):
    # print parameters from request
    callsign =  event["queryStringParameters"].get("callsign", "5BUU3")  

    # connect to postgres database
    print('Connecting to postgres database')
    db_url = f"postgresql://{os.environ.get('user')}:{os.environ.get('pass')}@{os.environ.get('host')}/{os.environ.get('dbname')}"
    engine = sqlalchemy.create_engine(db_url)
    print('Connected to postgres database')

    # get list of tables in database
    print('Getting list of tables in database')
    tables = engine.table_names()

    # get only timestamp from tables
    print('Getting only timestamp from tables')
    table_timestamps = [float(table.split('pace_data_')[1]) for table in tables]

    # get latest timestamp from table_timestamps
    print('Getting latest timestamp from table_timestamps')
    latest_timestamp = max(table_timestamps)

    # get data from the table with the latest timestamp
    print('Getting data from the table with the latest timestamp')
    table_name = f'pace_data_{int(latest_timestamp)}'

    # get data from the table where CallSign = callsign
    print('Getting all data from the table where CallSign = callsign')
    df = pd.read_sql(f"SELECT * FROM {table_name} WHERE \"CallSign\" like '%%{callsign}%%'", engine)
    # convert data to json
    print('Converting data to json')
    data = df.to_json(orient='records')
    print('Data converted to json')

    # return json data
    print('Returning json data')

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers" : "*",
            "Access-Control-Allow-Methods": "GET"
        },
        "body": json.dumps(data)
    }



    

    

        



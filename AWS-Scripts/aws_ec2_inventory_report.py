import boto3
from configparser import ConfigParser
from botocore.session import Session
import csv
from csv import DictWriter
from datetime import datetime, timedelta, timezone, date
from pprint import pprint
import os

def create_reports_dir():
    # Get the current date in the format 'YYYY-MM-DD'
    today_date = datetime.now().strftime('%Y-%m-%d')

    # Define the directory name
    directory_name = f"reports_{today_date}"

    # Get the current script's directory
    script_directory = os.path.dirname(os.path.realpath(__file__))

    # Create the full path for the new directory
    new_directory_path = os.path.join(script_directory, directory_name)

    # Check if the directory already exists
    if not os.path.exists(new_directory_path):
        # Create the directory
        os.makedirs(new_directory_path)
        print(f"Directory '{directory_name}' created at: {new_directory_path}")
    else:
        print(f"Directory '{directory_name}' already exists at: {new_directory_path}")

    return directory_name    

def filecheck(file):
    #check to see if file currently exists if so remove it and if not move toward creating it 
    if os.path.exists(file):
        os.remove(file) 

def main():
    # Read AWS credentials file
    config = ConfigParser()
    config.read('C:\\Users\\dmit27\\.aws\\credentials')  # Update with the correct path if needed

    new_dir = create_reports_dir()
    file_name = "ec2-AllTags-report" + str(date.today()) + ".csv"
    file_path = os.path.join(new_dir, file_name)
    filecheck(file_path)
    
    # Get the list of profile names
    profiles = config.sections()

    # Iterate through each profile
    for profile in config.sections():

        session = Session(profile=profile)

        credentials = session.get_credentials()

        region = 'us-west-2'

        sesh = boto3.Session(
            aws_access_key_id=credentials.access_key,
            aws_secret_access_key=credentials.secret_key,
            region_name=region
        )

    # Printing All Profiles in creds file 
        print(f"Processing profile: {profile}")

        # Put Check here 
        # Create an EC2 client
        ec2_client = boto3.client('ec2')

        resultsdict = {}

        # Get all instances
        response = ec2_client.describe_instances()
        instances = [instance for reservation in response['Reservations'] for instance in reservation['Instances']]

        # Collect all unique tag keys
        tag_keys = set()
        for instance in instances:
            tags = instance.get('Tags', [])
            for tag in tags:
                tag_keys.add(tag['Key']) 

        # Write tags to a CSV file
        with open(file_path, 'w', newline='') as csvfile:
            fieldnames = ['Profile','Instance_ID', 'Instance_Type', 'Status'] + list(tag_keys)  # Include 'Instance ID' as the first column
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for instance in instances:
                tags = {tag['Key']: tag['Value'] for tag in instance.get('Tags', [])}
                tags['Profile'] = profile
                tags['Instance_ID'] = instance['InstanceId']
                tags['Instance_Type'] = instance['InstanceType']
                tags['Status'] = instance['State'] ['Name']
                writer.writerow(tags)   

if __name__ == "__main__":
    main()

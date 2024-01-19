import boto3
from configparser import ConfigParser
from botocore.session import Session
import csv
from csv import DictWriter
from datetime import datetime, timedelta, timezone, date
from pprint import pprint
import os

# Creates a new directory for the reports
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


def write_to_csv(csvname, data):
    header = ['Profile', 'Instance ID', 'Instance Name', 'Hostname', 'Environment', 'Application', 'OS', 'Status',  'Instance Health Check','System Health Check']
    with open(csvname, 'a', newline='') as csvfile:
                writer = DictWriter(csvfile, fieldnames=header)
                if not os.path.exists(csvname) or os.path.getsize(csvname) ==0:
                    writer.writeheader()
                writer.writerow(data)
 



def main():
    # Read AWS credentials file
    config = ConfigParser()
    config.read('Put path to .aws\\credentials file here')  # Update with the correct path if needed

    new_dir = create_reports_dir()
    file_name = "ec2-health-check-report" + str(date.today()) + ".csv"
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

        # Get instance status
        instance_ids = [instance['InstanceId'] for instance in instances]
        status_response = ec2_client.describe_instance_status(InstanceIds=instance_ids)

        # Print the status details
        for instance_status in status_response['InstanceStatuses']:
            instance_id = instance_status['InstanceId']
            ec2_status = instance_status['InstanceState'] ['Name']
            system_status = instance_status['SystemStatus']['Status']
            instance_status = instance_status['InstanceStatus']['Status']

            # Get instance details
            instance = next((i for i in instances if i['InstanceId'] == instance_id), None)
            name_tag = next((tag['Value'] for tag in instance.get('Tags', []) if tag['Key'] == 'Name'), 'N/A')
            hostname_tag = next((tag['Value'] for tag in instance.get('Tags', []) if tag['Key'] == 'Hostname'), 'N/A')
            environment_tag = next((tag['Value'] for tag in instance.get('Tags', []) if tag['Key'] == 'Environment'), 'N/A')
            application_tag = next((tag['Value'] for tag in instance.get('Tags', []) if tag['Key'] == 'Application'), 'N/A')
            OS_tag = next((tag['Value'] for tag in instance.get('Tags', []) if tag['Key'] == 'OS'), 'N/A')
            

            resultsdict = {
                'Profile' : profile,
                'Instance ID': instance_id,
                'Instance Name': name_tag,
                'Hostname': hostname_tag,
                'Environment': environment_tag,
                'Application': application_tag,
                'OS': OS_tag,
                'Status': ec2_status,
                'System Health Check': system_status,
                'Instance Health Check': instance_status
            }

        
            results = resultsdict.copy()
#            pprint(results)
            write_to_csv(file_path,results)

if __name__ == "__main__":
    main()

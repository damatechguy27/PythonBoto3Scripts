import boto3
import csv
from datetime import date

# Initialize AWS session and EC2 client
#session = boto3.Session(
#    aws_access_key_id='YOUR_ACCESS_KEY',
#    aws_secret_access_key='YOUR_SECRET_KEY',
#    region_name='us-east-1'  # Replace with your desired region
#)

#ec2 = session.client('ec2')

file_name = "allec2-tags-" + str(date.today()) + ".csv"

# Get a list of all EC2 instances
ec2_cli = boto3.client('ec2', region_name="us-west-2")

response = ec2_cli.describe_instances()
instances = [instance for reservation in response['Reservations'] for instance in reservation['Instances']]

# Collect all unique tag keys
tag_keys = set()
for instance in instances:
    tags = instance.get('Tags', [])
    for tag in tags:
        tag_keys.add(tag['Key'])

# Write tags to a CSV file
with open(file_name, 'w', newline='') as csvfile:
    fieldnames = ['Instance_ID', 'Instance_Type', 'Status'] + list(tag_keys)  # Include 'Instance ID' as the first column
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for instance in instances:
        tags = {tag['Key']: tag['Value'] for tag in instance.get('Tags', [])}
        tags['Instance_ID'] = instance['InstanceId']
        tags['Instance_Type'] = instance['InstanceType']
        tags['Status'] = instance['State'] ['Name']
        writer.writerow(tags)

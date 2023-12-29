import boto3
from configparser import ConfigParser
from datetime import datetime, timedelta, date
import csv

# Read AWS credentials file
config = ConfigParser()
config.read('path to .aws.credentials')  # Update with the correct path if needed

# Get the list of profile names
profiles = config.sections()

# Calculate the date 90 days ago
ninety_days_ago = datetime.now() - timedelta(days=90)

# Create an empty list to store snapshot information
snapshot_info_list = []

# Iterate through each profile
for profile in profiles:
    print(f"Processing profile: {profile}")

    # Use the boto3 library with the current profile
    session = boto3.Session(profile_name=profile)
    ec2_client = session.client('ec2')

    # Example: List all EC2 snapshots
    response = ec2_client.describe_snapshots(OwnerIds=['self']) #ec2_client.describe_snapshots()
    snapshots = response['Snapshots']

    for snapshot in snapshots:
        start_time = snapshot['StartTime']
        # Convert the start time to a datetime object
        start_time_dt = start_time.replace(tzinfo=None)

        # Check if the snapshot is older than 90 days
        if start_time_dt < ninety_days_ago:
            snapshot_info = {
                'Profile': profile,
                'Snapshot ID': snapshot['SnapshotId'],
                'Volume ID': snapshot['VolumeId'],
                'Size (GB)': snapshot['VolumeSize'],
                'Start Time': start_time,
                'Encrypted': snapshot.get('Encrypted', 'N/A')
            }
            snapshot_info_list.append(snapshot_info)

# Write the list of dictionaries to a CSV file
csv_file_path = "ec2-snapshot-info" + str(date.today()) + ".csv"
fieldnames = ['Profile', 'Snapshot ID', 'Volume ID','Size (GB)', 'Start Time', 'Encrypted']

with open(csv_file_path, 'w', newline='') as csv_file:
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(snapshot_info_list)

print(f"Results exported to {csv_file_path}")

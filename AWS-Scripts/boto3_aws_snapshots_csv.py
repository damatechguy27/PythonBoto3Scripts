import boto3
import csv
from datetime import datetime, timedelta, timezone

def list_old_snapshots(region='us-east-1', retention_days=90):
    # Create an EC2 client
    ec2_client = boto3.client('ec2', region_name=region)

    # Calculate the date 3 months ago
    retention_date = datetime.now(timezone.utc) - timedelta(days=retention_days)

    # List all snapshots
    response = ec2_client.describe_snapshots(OwnerIds=['self'])

    # Filter snapshots older than retention_date
    old_snapshots = [snapshot for snapshot in response['Snapshots'] if snapshot['StartTime'] < retention_date]

    return old_snapshots

def export_to_csv(snapshots, output_file='old_AWS_snapshots.csv'):
    fieldnames = ['Snapshot Name', 'Snapshot ID', 'Size (GB)', 'Start Time', 'Encrypted']

    with open(output_file, 'w', newline='') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        for snapshot in snapshots:
            writer.writerow({
                'Snapshot Name': snapshot.get('Tags', [{}])[0].get('Value', 'N/A'),
                'Snapshot ID': snapshot['SnapshotId'],
                'Size (GB)': snapshot['VolumeSize'],
                'Start Time': snapshot['StartTime'],
                'Encrypted': snapshot['Encrypted']
            })

if __name__ == "__main__":
    # Replace 'your-region' with the AWS region you want to check
    region_to_check = 'us-west-2'

    # Replace '90' with the desired retention period in days
    retention_days_to_check = 90

    old_snapshots = list_old_snapshots(region=region_to_check, retention_days=retention_days_to_check)
    export_to_csv(old_snapshots)
    print(f"Snapshot details exported to 'old_snapshots.csv'")

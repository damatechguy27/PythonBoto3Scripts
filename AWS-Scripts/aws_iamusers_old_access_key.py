import boto3
from configparser import ConfigParser
from botocore.session import Session
import csv
from csv import DictWriter
from datetime import datetime, date
import os
from pathlib import Path 

def create_reports_dir():
    today_date = datetime.now().strftime('%Y-%m-%d')
    directory_name = f"reports_{today_date}"
    directory_path = Path(r'path you want folder to be created')
    full_directory_path = directory_path / directory_name 

    if not full_directory_path.exists():
        full_directory_path.mkdir(parents=True, exist_ok=True)
        print(f"Directory '{directory_name}' created at: {directory_path}")
    else:
        print(f"Directory '{directory_name}' already exists at: {directory_path}")

    return full_directory_path

def filecheck(file):
    if os.path.exists(file):
        os.remove(file)

def write_to_csv_noaccesskeys(csvname, users, profile, iam):
    header = ['Profile', 'Username']
    file_exists = os.path.exists(csvname) and os.path.getsize(csvname) > 0

    with open(csvname, 'a', newline='') as csvfile:
        writer = DictWriter(csvfile, fieldnames=header)
        if not file_exists:
            writer.writeheader()

        for user in users:
            username = user['UserName']
            account_profile = profile

            # Check if the user has access keys
            access_keys = iam.list_access_keys(UserName=username)['AccessKeyMetadata']

            if not access_keys:
                writer.writerow({'Profile': account_profile, 'Username': username})

def write_to_csv_old_accesskey(csvname, users, profile, iam):
    header = ['Profile', 'Username', 'AccessKeyId', 'CreateDate']
    file_exists = os.path.exists(csvname) and os.path.getsize(csvname) > 0

    with open(csvname, 'a', newline='') as csvfile:
        writer = DictWriter(csvfile, fieldnames=header)
        if not file_exists:
            writer.writeheader()

        for user in users:
            username = user['UserName']
            account_profile = profile
            access_keys = user.get('AccessKeys', [])

            for access_key in access_keys:
                access_key_id = access_key['AccessKeyId']
                create_date_str = access_key['CreateDate'].strftime('%Y-%m-%d %H:%M:%S')
                create_date = access_key['CreateDate']

                # Check if the access key is older than 90 days
                if datetime.now() - create_date > timedelta(days=90):
                    writer.writerow({'Profile': account_profile, 'Username': username, 'AccessKeyId': access_key_id, 'CreateDate': create_date_str})


def main():
    config = ConfigParser()
    config.read('path to creds file')

    new_dir = create_reports_dir()
    file_name_noaccesskeys = f"iam_users_with_noaccess_keys_{date.today()}.csv"
    file_name_old_accesskeys = f"iam_users_old_access_keys_{date.today()}.csv"
    file_path_noaccesskeys = new_dir / file_name_noaccesskeys
    file_path_old_accesskeys = new_dir / file_name_old_accesskeys
    filecheck(file_path_noaccesskeys)
    filecheck(file_path_old_accesskeys)

    for profile in config.sections():
        session = Session(profile=profile)
        credentials = session.get_credentials()
        region = 'region here'
        sesh = boto3.Session(
            aws_access_key_id=credentials.access_key,
            aws_secret_access_key=credentials.secret_key,
            region_name=region
        )

        print(f"Processing profile: {profile}")

        iam = sesh.client('iam')
        response = iam.list_users()
        users_without_keys = [user for user in response['Users'] if not user.get('AccessKeys')]
        write_to_csv_noaccesskeys(file_path_noaccesskeys, users_without_keys, profile, iam)

        users_with_old_keys = [user for user in response['Users'] if user.get('AccessKeys')]
        write_to_csv_old_accesskey(file_path_old_accesskeys, users_with_old_keys, profile, iam)

    print(f"Data written to '{file_path_noaccesskeys}'")
    print(f"Data written to '{file_path_old_accesskeys}'")
if __name__ == "__main__":
    main()

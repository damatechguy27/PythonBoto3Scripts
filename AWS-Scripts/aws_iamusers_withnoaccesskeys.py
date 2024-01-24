import boto3
from configparser import ConfigParser
from botocore.session import Session
import csv
from csv import DictWriter
from datetime import datetime, date
import os

def create_reports_dir():
    today_date = datetime.now().strftime('%Y-%m-%d')
    directory_name = f"reports_{today_date}"
    script_directory = os.path.dirname(os.path.realpath(__file__))
    new_directory_path = os.path.join(script_directory, directory_name)

    if not os.path.exists(new_directory_path):
        os.makedirs(new_directory_path)
        print(f"Directory '{directory_name}' created at: {new_directory_path}")
    else:
        print(f"Directory '{directory_name}' already exists at: {new_directory_path}")

    return directory_name

def filecheck(file):
    if os.path.exists(file):
        os.remove(file)

def write_to_csv(csvname, users, profile):
    header = ['Profile', 'Username']
    file_exists = os.path.exists(csvname) and os.path.getsize(csvname) > 0

    with open(csvname, 'a', newline='') as csvfile:
        writer = DictWriter(csvfile, fieldnames=header)
        if not file_exists:
            writer.writeheader()

        for user in users:
            username = user['UserName']
            account_profile = profile
            writer.writerow({'Profile': account_profile, 'Username': username})


def main():
    config = ConfigParser()
    config.read('Path to aws creds file')

    new_dir = create_reports_dir()
    file_name = f"iam_users_with_noaccess_keys_{date.today()}.csv"
    file_path = os.path.join(new_dir, file_name)
    filecheck(file_path)

    for profile in config.sections():
        session = Session(profile=profile)
        credentials = session.get_credentials()
        region = 'us-west-2'
        sesh = boto3.Session(
            aws_access_key_id=credentials.access_key,
            aws_secret_access_key=credentials.secret_key,
            region_name=region
        )

        print(f"Processing profile: {profile}")

        iam = sesh.client('iam')
        response = iam.list_users()
        users_without_keys = [user for user in response['Users'] if not user.get('AccessKeys')]
        write_to_csv(file_path, users_without_keys, profile)

    print(f"Data written to '{file_path}'")

if __name__ == "__main__":
    main()

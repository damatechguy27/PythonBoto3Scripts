import boto3
import os
import gzip
import shutil
import tempfile
from botocore.exceptions import NoCredentialsError
from datetime import datetime, timedelta

def pull_logs_and_export(log_group_names, s3_bucket_name, excluded_log_groups=None, last_event_timestamp=None):
    # Set up Boto3 clients
    cloudwatch_logs_client = boto3.client('logs')
    s3_client = boto3.client('s3')

    for log_group_name in log_group_names:
        # Create a temporary directory to store log files
        temp_dir = tempfile.mkdtemp()

        try:
            # Get the latest log stream in the CloudWatch Log Group
            response = cloudwatch_logs_client.describe_log_streams(
                logGroupName=log_group_name,
                orderBy='LastEventTime',
                descending=True,
                limit=1
            )

            if not response['logStreams']:
                # No log streams found in the log group
                continue

            log_stream_name = response['logStreams'][0]['logStreamName']

            # Get the log events from the log stream
            start_time = last_event_timestamp or 0
            log_events_response = cloudwatch_logs_client.get_log_events(
                logGroupName=log_group_name,
                logStreamName=log_stream_name,
                startTime=start_time,
                limit=100  # Adjust the limit as needed
            )

            # Update last event timestamp
            if log_events_response['events']:
                last_event_timestamp = log_events_response['events'][-1]['timestamp'] + 1

            # Write log events to a temporary file
            temp_log_file = os.path.join(temp_dir, 'logs.txt')
            with open(temp_log_file, 'w') as f:
                for event in log_events_response['events']:
                    f.write(event['message'] + '\n')

            # Compress the log file
            compressed_log_file = temp_log_file + '.gz'
            with open(temp_log_file, 'rb') as f_in, gzip.open(compressed_log_file, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)

            # Upload the compressed log file to S3
            s3_key = f"{log_group_name}/{log_stream_name}/{compressed_log_file}"
            s3_client.upload_file(compressed_log_file, s3_bucket_name, s3_key)

        except NoCredentialsError:
            print(f"Credentials not available for log group: {log_group_name}")

        finally:
            # Clean up temporary directory
            shutil.rmtree(temp_dir)

def lambda_handler(event, context):
    # Replace with your S3 bucket name
    s3_bucket_name = 'your-s3-bucket-name'

    # Replace with a list of CloudWatch Log Groups to exclude, or set to None to include all
    excluded_log_groups = ['/aws/lambda/excluded_function']

    # Replace with the last event timestamp from the previous run
    last_event_timestamp = datetime.timestamp(datetime.now() - timedelta(days=1))

    # Replace with your list of CloudWatch Log Group names
    log_group_names = ['/aws/lambda/lambda_function_1', '/aws/lambda/lambda_function_2']

    pull_logs_and_export(log_group_names, s3_bucket_name, excluded_log_groups, last_event_timestamp)

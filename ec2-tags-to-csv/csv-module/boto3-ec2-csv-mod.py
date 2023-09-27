import boto3
from pprint import pprint
from datetime import date
from csv import DictWriter
import os
ec2_cli = boto3.client('ec2', region_name="us-west-2")

response1 = ec2_cli.describe_instances()['Reservations']

vm_id = ''
vm_type = ''
vm_status = ''
vm_name = ""
vm_env = ""
vm_owner = ""

resultsdict = {}
file_name = "ec2-dict-" + str(date.today()) + ".csv"
header_added = False
header = ['Instance_ID', 'Instance_Type', 'Status','Name','Environment','Owner']

#Checks to make sure a current report does not exist 
if os.path.exists(file_name):
    os.remove(file_name)
    print("File found and removed....")
else:
    print("No File was found")

# Gathers the information from the Boto3 Cli tool to grab information needed 
for each_inst in response1:
    for each_ec2 in each_inst['Instances']:
    
        vm_id = each_ec2['InstanceId']
        vm_type = each_ec2['InstanceType']
        vm_status = each_ec2['State'] ['Name']
        for all_tags in each_ec2['Tags']:

            if all_tags["Key"] == "Name":
                inst_name = all_tags['Value']

                vm_name = inst_name
            if all_tags["Key"] == "Environment": 
                inst_env = all_tags['Value']

                vm_env = inst_env
            if all_tags["Key"] == "Owners":
                inst_owner = all_tags['Value']

                vm_owner = inst_owner

#Puts the result into the dictionary variable below        
        resultsdict = {
                'Instance_ID': vm_id,
                'Instance_Type': vm_type,
                'Status': vm_status,   
                'Name' : vm_name,
                'Environment' : vm_env,
                'Owner' : vm_owner 
                }        


        
    print(resultsdict)
   
    
#Creates the CSV file to put the data into     
    with open(file_name, 'a') as csvfile:
        writer = DictWriter(csvfile, fieldnames=header)
        if not header_added:
            writer.writeheader()
            header_added = True
        
        writer.writerow(resultsdict)
        csvfile.close()

header_added = False
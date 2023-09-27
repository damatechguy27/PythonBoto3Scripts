import boto3
from pprint import pprint
import pandas as pd
import os

vm_id = ''
vm_type = ''
vm_status = ''
vm_name = ""
vm_env = ""
vm_owner = ""
resultsdict = {}

file_name = "ec2-test.csv"

def filecheck(file):
    #Checks to make sure a current report does not exist 
    if os.path.exists(file):
        os.remove(file)
        print("File found and removed....")
    else:
        print("No File was found")

def pullEc2Infotocsv(csvname):
    # Gathers the information from the Boto3 Cli tool to grab information needed 
    ec2_cli = boto3.client('ec2', region_name="us-west-2")
    response1 = ec2_cli.describe_instances()['Reservations']
    global resultsdict
    global vm_id
    global vm_type
    global vm_status
    global vm_name
    global vm_env 
    global vm_owner
    header_added = False    
    header = ['Instance_ID', 'Instance_Type', 'Status','Name','Environment','Owner']

    for each_inst in response1:
        for each_ec2 in each_inst['Instances']:
            

            vm_id = each_ec2['InstanceId']
            vm_type = each_ec2['InstanceType']
            vm_status = each_ec2['State'] ['Name']

            for all_tags in each_ec2['Tags']:

                if all_tags["Key"] == "Name":
                    vm_name = all_tags['Value']

                if all_tags["Key"] == "Environment": 
                    vm_env = all_tags['Value']

                if all_tags["Key"] == "Owners":
                    vm_owner = all_tags['Value']

    #Puts the result into the dictionary variable below                
            resultsdict = {
                    'Instance_ID': [vm_id],
                    'Instance_Type': [vm_type],
                    'Status': [vm_status],   
                    'Name' : [vm_name],
                    'Environment' : [vm_env],
                    'Owner' : [vm_owner] 
                    }   

    #Adds the data into a Pandas dataframe
            results = pd.DataFrame(resultsdict)
            
            
    #Creates the CSV file to put the data into    
            if not header_added:
                
                results.to_csv(csvname, index=False, mode='a', header=True)
                header_added = True
            else:
                results.to_csv(csvname, index=False, mode='a', header=False)

    header_added = False


filecheck(file_name)       
    
pullEc2Infotocsv(file_name) 
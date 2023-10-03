import boto3
from pprint import pprint
import csv
from csv import DictWriter
from fuzzywuzzy import fuzz
from datetime import date
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
header = ['Instance_ID', 'Instance_Type', 'Status','Name','Environment','Owner', 'Conventions', 'Hostname-tag-check', 'Audit-pass']

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


        
    #print(resultsdict)
   
  
#Creates the CSV file to put the data into     
    with open(file_name, 'a') as csvfile:
        writer = DictWriter(csvfile, fieldnames=header)
        if not header_added:
            writer.writeheader()
            header_added = True
            #print(header_added)
        
        writer.writerow(resultsdict)


        csvfile.close()

header_added = False
#print(header_added)
##########################################################
#adding naming conventions to compare 
##########################################################

input_file = file_name

with open(input_file, 'r+') as csv_file:
    # Read the existing data and add "conventions" column header
    reader = csv.DictReader(csv_file)
    fieldnames = reader.fieldnames #+ ['Conventions']
    data = list(reader)

    # Add values to the "conventions" column in existing rows
    for row in data:
        row['Conventions'] = 'ASG-xxx'

    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    csv_file.seek(0)  # Move the cursor to the beginning of the file
    writer.writeheader()  # Write the header row
    writer.writerows(data)  # Write the modified data

#########################################################
##########################################################
#CHECKS IF CSV COLUMNS 1 AND 2  are similar 
##########################################################
with open(input_file, 'r+') as csv_file:
    # Read the existing data and add "Hostname-tag-check" column header
    reader = csv.DictReader(csv_file)
    fieldnames = reader.fieldnames #+ ['Hostname-tag-check']
    data = list(reader)

    # Compare values and write to "Hostname-tag-check" column
    for row in data:
        column1_value = row['Name']
        column2_value = row['Instance_ID']

        # Implement your comparison logic here using fuzzywuzzy
        similarity = fuzz.ratio(column1_value.lower(), column2_value.lower())

        # Set the "Hostname-tag-check" column to True if similar, else False
        row['Hostname-tag-check'] = str(similarity >= 25)  # Adjust the threshold as needed

    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    csv_file.seek(0)  # Move the cursor to the beginning of the file
    writer.writeheader()  # Write the header row
    writer.writerows(data)  # Write the modified data


###################################################################
# CHECKS IF CSV COLUMNS 1 AND 2 ARE FOLLOING A NAMING CONVENTIONS 
###################################################################
# Function to compare a value to a naming convention


# Input CSV file name
input_file = file_name

with open(input_file, 'r+') as csv_file:
    # Read the existing data and add "audit_check" column header
    reader = csv.DictReader(csv_file)
    fieldnames = reader.fieldnames #+ ['Audit-pass']
    data = list(reader)

    # Compare values and write to "audit_check" column
    for row in data:
        column1_value = row['Name']
        #column2_value = row['Instance_ID']
        naming_convention = 'Audit-pass'  # Replace with your convention

        similarity1 = fuzz.partial_ratio(column1_value.lower(), naming_convention.lower())
        #similarity2 = fuzz.partial_ratio(column2_value.lower(), naming_convention.lower())

        row['Audit-pass'] = str(similarity1 >= 25)#and similarity2 >= 25

    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    csv_file.seek(0)  # Move the cursor to the beginning of the file
    writer.writeheader()  # Write the header row
    writer.writerows(data)  # Write the modified data

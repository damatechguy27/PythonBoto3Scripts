from pprint import pprint
from datetime import date


file_name = "ec2-dict-" + str(date.today()) + ".csv"

def filecheck(file):
    import os
    #check to see if file currently exists if so remove it and if not move toward creating it 
    if os.path.exists(file):
        os.remove(file)
        print("File found and removed....")
    else:
        print("No File was found")

def pullEc2Info(csvname):
    #pulls ec2 tags and puts them into a dictionary and writes the output to an csv 
    import boto3
    from csv import DictWriter

    ec2_cli = boto3.client('ec2', region_name="us-west-2")
    response1 = ec2_cli.describe_instances()['Reservations']
    resultsdict = {}
    vm_id = ''
    vm_type = ''
    vm_status = ''
    vm_name = ""
    vm_env = ""
    vm_owner = ""


    header_added = False    
    header = ['Instance_ID', 'Instance_Type', 'Status','Name','Environment','Owner']
    
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
       
        
       
    #Creates the CSV file to put the data into
        with open(csvname, 'a') as csvfile:
            writer = DictWriter(csvfile, fieldnames=header)
            if not header_added:
                writer.writeheader()
                header_added = True
                
                
            writer.writerow(resultsdict)
            csvfile.close()

    header_added = False
    

def addcsv_naming_conv(csvname):
    import csv
    
    #adds the naming conventions column into csv is not already added 
    # adds the correct naming convention to compare with in newly created column
    with open(csvname, 'r+') as csv_file:
        # Read the existing data and add "conventions" column header
        reader = csv.DictReader(csv_file)
        fieldnames = reader.fieldnames + ['Conventions']
        data = list(reader)

        # Add values to the "conventions" column in existing rows
        for row in data:
            row['Conventions'] = 'ASG-xxx'

        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        csv_file.seek(0)  # Move the cursor to the beginning of the file
        writer.writeheader()  # Write the header row
        writer.writerows(data)  # Write the modified data

def comp_hostname_to_tag(csvname):
    import csv
    from fuzzywuzzy import fuzz


    #adds the hostname-tag-check column into csv is not already added 
    # checks to see if the value in column match then write true or false into newly created column
    
    with open(csvname, 'r+') as csv_file:
    # Read the existing data and add "Hostname-tag-check" column header
        reader = csv.DictReader(csv_file)
        fieldnames = reader.fieldnames + ['Hostname-tag-check']
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

def namingconv_audit_check(csvname):
    import csv
    from fuzzywuzzy import fuzz

    #adds the audit-pass column into csv is not already added 
    # checks to see if the value in columns match then write true or false into newly created column

    with open(csvname, 'r+') as csv_file:
        # Read the existing data and add "audit_check" column header
        reader = csv.DictReader(csv_file)
        fieldnames = reader.fieldnames + ['Audit-pass']
        data = list(reader)

        # Compare values and write to "audit_check" column
        for row in data:
            column1_value = row['Name']
            
            naming_convention = 'Audit-pass'  # Replace with your convention

            similarity1 = fuzz.partial_ratio(column1_value.lower(), naming_convention.lower())
            

            row['Audit-pass'] = str(similarity1 >= 25)

        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        csv_file.seek(0)  # Move the cursor to the beginning of the file
        writer.writeheader()  # Write the header row
        writer.writerows(data)  # Write the modified data

filecheck(file_name)       
    
pullEc2Info(file_name) 

addcsv_naming_conv(file_name)

comp_hostname_to_tag(file_name)

namingconv_audit_check(file_name)

def filecheck(file):
    import os
    #check to see if file currently exists if so remove it and if not move toward creating it 
    if os.path.exists(file):
        os.remove(file)
        #print("File found and removed....")
    #else:
        #print("No File was found")

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
    vm_hostname = ''
    vm_env = ""
    vm_owner = ""


    header_added = False    
    header = ['Instance_ID', 'Instance_Type', 'Status','Name','HOSTNAME','ENVIRONMENT','Owner']
    
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
                if all_tags["Key"] == "HOSTNAME":
                    inst_hostname = all_tags['Value']

                    vm_hostname = inst_hostname
                if all_tags["Key"] == "ENVIRONMENT": 
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
                   'HOSTNAME':vm_hostname,
                   'ENVIRONMENT' : vm_env,
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
            row['Conventions'] = 'LLL-NNN-FFF-EE-SS'

        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        csv_file.seek(0)  # Move the cursor to the beginning of the file
        writer.writeheader()  # Write the header row
        writer.writerows(data)  # Write the modified data

def comp_hostname_to_tag(csvname):
    import csv
    from fuzzywuzzy import fuzz


    #adds the hostname-tag-check column into csv is not already added 
    # checks to see if the value in column match then write true or false into newly created column

# Function to compare values while ignoring delimiters
    def compare_without_delimiters(name, hostname):
        # Remove delimiters from "Name" and "Hostname" for comparison
        name_without_delimiters = name.replace('.', '')
        hostname_without_delimiters = hostname.replace('.', '')
        return fuzz.ratio(name_without_delimiters.lower(), hostname_without_delimiters.lower()) >= 100

    # Open the CSV file for reading and writing
    with open(csvname, 'r') as csv_file:
        # Read the existing data and add "Hostname-tag-check" column header
        reader = csv.DictReader(csv_file)
        fieldnames = reader.fieldnames + ['Hostname-tag-check']
        data = list(reader)

    # Compare values and write to "Hostname-tag-check" column
    for row in data:
        column1_value = row['Name']
        column2_value = row['HOSTNAME']
        row['Hostname-tag-check'] = str(compare_without_delimiters(column1_value, column2_value))

    # Write the modified data back to the CSV file
    with open(csvname, 'w', newline='') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)


def namingconv_audit_check(csvname, csvauditfile):
    import csv

    # Define your naming conventions
    allowedlocations = ['NBA', 'NFL', 'NHL']
    name_length = 20
    allowedfuncs = ['WEB', 'MAR', 'VCR', 'DVD']
    allowedenv = ['DC', 'VA', 'CA', 'FL', 'SS']
    #allowedseq = ['ss', 'ts', 'cr', 'VD']

    # Function to check if a value matches the naming conventions
    def matches_naming_conventions(name):
        parts = name.split('.')
        if len(parts) != 4:
            return False  # A valid name should have exactly 5 parts separated by periods

        location, appname, func, envSeq = parts
        env = envSeq[:2]
        seq = envSeq.replace(env,"")
        if (
            location in allowedlocations
            and len(appname) <= name_length
            and func in allowedfuncs
            and env in allowedenv
            and seq.isdigit() and 1 <= int(seq) <= 99
        ):
            return "True"
        return "False"

    # Input and output file paths
    input_file = csvname  # Replace with your input CSV file
    output_file = csvauditfile  # Replace with your output CSV file

    # Read the input CSV file and check the "names" column
    with open(input_file, 'r', newline='') as csv_input, open(output_file, 'w', newline='') as csv_output:
        reader = csv.DictReader(csv_input)
        fieldnames = reader.fieldnames + ["audit check"]  # Add "audit check" column to the output

        writer = csv.DictWriter(csv_output, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            name = row["Name"]
            audit_check = matches_naming_conventions(name)
            row["audit check"] = audit_check
            writer.writerow(row)

    print("Audit check completed. Results written to", output_file)


def main():
    from pprint import pprint
    from datetime import date


    file_name = "ec2-dict-" + str(date.today()) + ".csv"

    audit_check_file_name = "ec2-nc-auditcheck" + str(date.today()) + ".csv"

    filecheck(file_name)

    filecheck(audit_check_file_name)       
        
    pullEc2Info(file_name) 

    addcsv_naming_conv(file_name)

    comp_hostname_to_tag(file_name)

    namingconv_audit_check(file_name, audit_check_file_name)

    filecheck(file_name)

if __name__ == "__main__":
    main()
def lambda_handler(event, context):
    import boto3
    from datetime import date
    #import csv 
    from csv import DictWriter
    import os
    
    
    
    # Function to compare values while ignoring delimiters
    def compare_without_delimiters(name, hostname):
            # Remove delimiters from "Name" and "Hostname" for comparison
        name_without_delimiters = name.replace('.', '')
        hostname_without_delimiters = hostname.replace('.', '')
            #return fuzz.ratio(name_without_delimiters.lower(), hostname_without_delimiters.lower()) >= 100
        if name_without_delimiters == hostname_without_delimiters:
            return True
        return False
    
    
    
    def matches_naming_conventions(name):
            parts = name.split('.')
            if len(parts) != 4:
                return False  # A valid name should have exactly 5 parts separated by periods
    
            location, vmname, func, envSeq = parts
            env = envSeq[:2]
            seq = envSeq.replace(env,"")
            if (
                location in allowedlocations
                and len(vmname) <= name_length
                and func in allowedfuncs
                and env in allowedenv
                and seq.isdigit() and 1 <= int(seq) <= 99
            ):
                return "True"
            return "False"
    
    
    def package_csv_to_s3(bucket_name, data):
        
        global header_added
        header_added = False
        file_name = "ec2-dict-" + str(date.today()) + ".csv"
        file_path = "/tmp/ec2-dict-" + str(date.today()) + ".csv"
        with open(file_path, 'a') as csvfile:
                writer = DictWriter(csvfile, fieldnames=header)
                if not os.path.exists(file_path) or os.path.getsize(file_path) ==0:
                    writer.writeheader()
                writer.writerow(data)
    
        s3 = boto3.client('s3')
    
        s3.upload_file(file_path, bucket_name, file_name)
    
        # Gathers the information from the Boto3 Cli tool to grab information needed 
    ec2_cli = boto3.client('ec2', region_name="us-west-2")
    
    response1 = ec2_cli.describe_instances()['Reservations']
    
    s3_name = 'testscript-dam'
    
    vm_id = ''
    vm_type = ''
    vm_status = ''
    vm_name = ""
    vm_hostname = ''
    vm_env = ""
    vm_owner = ""
    
    resultsdict = {}
    #header_added = False
    header = ['Instance_ID', 'Instance_Type', 'Status','Name','HOSTNAME','ENVIRONMENT','Owner','Tag_comp_check', 'NC_Audit']
    # Define your naming conventions
    allowedlocations = ['NBA', 'NFL', 'NHL']
    name_length = 20
    allowedfuncs = ['WEB', 'MAR', 'VCR', 'DVD']
    allowedenv = ['DC', 'VA', 'CA', 'FL', 'SS']
    
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
                        'Owner' : vm_owner, 
                        'Tag_comp_check': str(compare_without_delimiters(vm_name,vm_hostname)),
                        'NC_Audit': matches_naming_conventions(vm_name)
                        }
           
    #copy the results of the dictionary
        results = resultsdict.copy()
    #print the result         
    #    print(results)
    #upload to s3
        package_csv_to_s3(s3_name, results)
        #print(resultsdict)

    return {
            'statusCode': 200,
            'body': 'EC2 instance statuses retrieved, printed to CSV, and uploaded to S3.'
        }       

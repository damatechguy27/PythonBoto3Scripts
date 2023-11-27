from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.resource import SubscriptionClient


def auth_to_azure():
    creds = DefaultAzureCredential()

    return creds
    
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

    # Define your naming conventions
    allowedlocations = ['NBA', 'NFL', 'NHL']
    name_length = 20
    allowedfuncs = ['WEB', 'MAR', 'VCR', 'DVD']
    allowedenv = ['DC', 'VA', 'CA', 'LA', 'AL']
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


def print_csv(csv_name, data):
    from csv import DictWriter
    import os
    header = ['VM Name', 'Name', 'Hostname', 'Tag_Check', 'NC_Audit']
    with open(csv_name, 'w', newline='') as csvfile:
        writer = DictWriter(csvfile, fieldnames=header)
        #                if not os.path.exists(file_path) or os.path.getsize(file_path) ==0:
        writer.writeheader()
        writer.writerows(data)



def get_name_hostname_tags_all_resource_groups(creds, csvname):
    credentials = creds
    subscription_client = SubscriptionClient(credentials)

    subs = subscription_client.subscriptions.list()

    vm_name = ''
    vm_hostname = ''
    global resultsdict
    resultsdict = {}
    global results
    results_list = []

    for sub in subs:

        # Create ResourceManagementClient to get resource groups
        resource_client = ResourceManagementClient(credentials, sub.subscription_id)
        # Get all resource groups
        resource_groups = resource_client.resource_groups.list()

        # Create ComputeManagementClient to get VMs
        compute_client = ComputeManagementClient(credentials, sub.subscription_id)

        # Iterate over each resource group and get VMs
        for resource_group in resource_groups:
            resource_group_name = resource_group.name
            #print(f"Resource Group: {resource_group_name}")

            # Get all VMs in the resource group
            vms = compute_client.virtual_machines.list(resource_group_name)

            # Iterate over each VM and retrieve name and hostname tags
            for vm in vms:
                #vm_name = vm.name
                tags = vm.tags
                if tags and 'Name' in tags and 'Hostname' in tags:
                    #name_tag = tags['Name']
                    vm_name = tags['Name']
                    
                    #hostname_tag = tags['Hostname']
                    vm_hostname = tags['Hostname']
                    
                    #print(f"  VM '{vm_name}' - Name: {name_tag}, Hostname: {hostname_tag}")

                    resultsdict = {
                        'VM Name': vm.name,
                        'Name': vm_name,
                        'Hostname': vm_hostname,
                        'Tag_Check' : str(compare_without_delimiters(vm_name,vm_hostname)),
                        'NC_Audit' : matches_naming_conventions(vm_name)
                    }
                    #return resultsdict
                    results_list.append(resultsdict)

    print_csv(csvname,results_list)
 #       return results_list






if __name__ == "__main__":

    from datetime import date

    creds = auth_to_azure()

    #results_data = get_name_hostname_tags_all_resource_groups(creds)

    filename = "azurevm_nc_check" + str(date.today()) + ".csv"
    
    results_data = get_name_hostname_tags_all_resource_groups(creds, filename)    
#    print_csv(filename, results_data)

from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.compute import ComputeManagementClient

def get_all_vm_tags():
    # Your Azure subscription ID
    subscription_id = 'SUB_ID'
    
    # Authenticate using the service principal
    credentials = DefaultAzureCredential()

    # Create the ResourceManagementClient to get a list of resource groups
    resource_client = ResourceManagementClient(credentials, subscription_id)

    # Get a list of all resource groups in the subscription
    resource_groups = resource_client.resource_groups.list()

    # Create the ComputeManagementClient to work with virtual machines
    compute_client = ComputeManagementClient(credentials, subscription_id)

    vm_tags_list = []
    all_tags = set()

    # Iterate over each resource group and get VMs
    for resource_group in resource_groups:
        resource_group_name = resource_group.name

        # Get all VMs in the resource group
        vms = compute_client.virtual_machines.list(resource_group_name)

        # Iterate over each VM and retrieve all tags
        for vm in vms:
            vm_name = vm.name
            tags = vm.tags
            if tags:
                # Collect all unique tags
                all_tags.update(tags.keys())
                # Append VM details and tags to the list
                vm_tags_list.append({
                    'ResourceGroup': resource_group_name,
                    'VMName': vm_name,
                    **tags  # Unpack tags as separate columns
                })

    return vm_tags_list, list(all_tags)

def print_csv(csv_name, data, header):
    from csv import DictWriter

    with open(csv_name, 'w', newline='') as csvfile:
        writer = DictWriter(csvfile, fieldnames=header)
        writer.writeheader()
        writer.writerows(data)

if __name__ == "__main__":
    
    from datetime import date
    
    vm_tags_data, tag_headers = get_all_vm_tags()

    filename = "azure_vm_tags" + str(date.today()) + ".csv"
    print_csv(filename, vm_tags_data, ['ResourceGroup', 'VMName'] + tag_headers)


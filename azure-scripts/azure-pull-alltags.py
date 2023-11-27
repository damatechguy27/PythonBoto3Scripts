from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.resource import SubscriptionClient

def auth_to_azure():
    creds = DefaultAzureCredential()

    return creds

def print_csv(csv_name, data, header):
    from csv import DictWriter

    with open(csv_name, 'w', newline='') as csvfile:
        writer = DictWriter(csvfile, fieldnames=header)
        writer.writeheader()
        writer.writerows(data)

def get_all_vm_tags(creds, csvname):
    credentials = creds
    subscription_client = SubscriptionClient(credentials)

    subs = subscription_client.subscriptions.list()
    
    vm_tags_list = []
    all_tags = set()


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

    print_csv(csvname, vm_tags_list, ['ResourceGroup', 'VMName'] + list(all_tags))


#        return vm_tags_list, list(all_tags)


if __name__ == "__main__":
    
    from datetime import date
    
    creds = auth_to_azure()

    filename = "azure_vm_tags" + str(date.today()) + ".csv"

    result_data = get_all_vm_tags(creds, filename)

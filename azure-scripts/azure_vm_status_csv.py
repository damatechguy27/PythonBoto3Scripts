from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.resource import SubscriptionClient
from datetime import datetime
import time


def auth_to_azure():
    creds = DefaultAzureCredential()

    return creds


def get_vm_subscriptions(creds):

    credentials = creds
    subscription_client = SubscriptionClient(credentials)

    subs = subscription_client.subscriptions.list()

    sub_ids = [subscription.subscription_id for subscription in subs]
        
        
    return sub_ids

def get_all_vm_status(creds, sub_id):
    # Use DefaultAzureCredential to authenticate
    credential = creds

    # Create ResourceManagementClient to get resource groups
    resource_client = ResourceManagementClient(credential, sub_id)

    # Get all resource groups
    resource_groups = resource_client.resource_groups.list()

    all_vm_status_info = []

    # Create ComputeManagementClient to get VMs
    compute_client = ComputeManagementClient(credential, sub_id)

    # Iterate through resource groups
    for resource_group in resource_groups:
        resource_group_name = resource_group.name

        # Get VMs in the current resource group
        vms = compute_client.virtual_machines.list(resource_group_name)

        # Iterate through VMs
        for vm in vms:
            vm_name = vm.name

            # Get VM instance view
            instance_view = compute_client.virtual_machines.instance_view(resource_group_name, vm_name)

            # Check the status of the VM
            power_state = instance_view.statuses[1].display_status if len(instance_view.statuses) > 1 else "Unknown"


            # Add VM status info to the list
            vm_status_info = {
                'Resource Group': resource_group_name,
                'VM Name': vm_name,
                'Power State': power_state,
                'VM Location': vm.location
            }
            all_vm_status_info.append(vm_status_info)

            #print(vm_status_info)
    return all_vm_status_info

def print_csv(csv_name, data):
    from csv import DictWriter
    import os
    header = ['VM Name', 'Resource Group', 'Power State', 'VM Location']
    with open(csv_name, 'w', newline='') as csvfile:
        writer = DictWriter(csvfile, fieldnames=header)
        writer.writeheader()
        writer.writerows(data)

if __name__ == "__main__":

    from datetime import date

    credentials = auth_to_azure()

    sub_ids = get_vm_subscriptions(credentials)

    print(sub_ids)

    filename = "azurevm_status_" + str(date.today()) + ".csv"
    
    vm_status_info_list = get_all_vm_status(credentials, ','.join(sub_ids))

    print_csv(filename, vm_status_info_list)
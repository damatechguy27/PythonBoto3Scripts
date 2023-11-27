from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.resource import SubscriptionClient
from datetime import datetime
import time


def auth_to_azure():
    creds = DefaultAzureCredential()

    return creds


def get_all_vm_status(creds):

    credentials = creds
    subscription_client = SubscriptionClient(credentials)

    subs = subscription_client.subscriptions.list()

    all_vm_status_info = []

    for sub in subs:

        # Create ResourceManagementClient to get resource groups
        resource_client = ResourceManagementClient(credentials, sub.subscription_id)
        # Get all resource groups
        resource_groups = resource_client.resource_groups.list()

        # Create ComputeManagementClient to get VMs
        compute_client = ComputeManagementClient(credentials, sub.subscription_id)
    

        # Iterate through resource groups
        for resource_group in resource_groups:
            resource_group_name = resource_group.name

            # Get VMs in the current resource group
            vms = compute_client.virtual_machines.list(resource_group_name)

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

    creds = auth_to_azure()

    vm_status_info_list = get_all_vm_status(creds)

    # Print the results
#    for info in vm_status_info_list:
#        print(f"Resource Group: {info['Resource Group']}, VM Name: {info['VM Name']}, Power State: {info['Power State']}, VM Location: {info['VM Location']}")

    filename = "azurevm_status_" + str(date.today()) + ".csv"

    print_csv(filename, vm_status_info_list)
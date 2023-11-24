from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.compute import ComputeManagementClient
from datetime import datetime
import time

'''
def get_last_power_off_time(vm):
    # Retrieve the last power-off time from the VM's instance view
    for status in vm.instance_view.statuses:
        if status.code == 'PowerState/stopped' and status.level == InstanceViewStatusLevelTypes.info:
            return status.time.strftime('%Y-%m-%d %H:%M:%S')
    return 'N/A'
'''

def get_all_vm_status():
    # Use DefaultAzureCredential to authenticate
    credential = DefaultAzureCredential()

    # Create ResourceManagementClient to get resource groups
    resource_client = ResourceManagementClient(credential, '6fb9af7b-a6e1-44e0-955d-595b9675e989')

    # Get all resource groups
    resource_groups = resource_client.resource_groups.list()

    all_vm_status_info = []

    # Create ComputeManagementClient to get VMs
    compute_client = ComputeManagementClient(credential, '6fb9af7b-a6e1-44e0-955d-595b9675e989')

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

            #powered_off_status = next((status for status in instance_view.statuses if status.code.startswith("PowerState/stopped")), None)
            #last_power_off_time = powered_off_status.time.strftime("%Y %m %d %H:%M:%S") if powered_off_status else "N/A"

            # Get the last update time of the VM instance
            #last_update_time = instance_view.time.strftime('%Y-%m-%d %H:%M:%S') if instance_view.time else "N/A"

            # Get the last update time of the VM instance
            last_update_time = None
            for status in instance_view.statuses:
                if status.code.startswith('PowerState/') and status.time:
                    last_update_time = status.time
                    break

            # Format the last update time
            last_update_time_str = last_update_time.strftime('%Y-%m-%d %H:%M:%S') if last_update_time else "N/A"


            # Add VM status info to the list
            vm_status_info = {
                'Resource Group': resource_group_name,
                'VM Name': vm_name,
                'Power State': power_state,
                'Last Updated': last_update_time_str,
                'VM Location': vm.location
                #'vm_status' : vm.instance_view.statuses[1].display_status
            }
            all_vm_status_info.append(vm_status_info)

    return all_vm_status_info

if __name__ == "__main__":
    vm_status_info_list = get_all_vm_status()

    # Print the results
    for info in vm_status_info_list:
        print(f"Resource Group: {info['Resource Group']}, VM Name: {info['VM Name']}, Power State: {info['Power State']}, Last Updated {info['Last Updated']}, VM Location: {info['VM Location']}")

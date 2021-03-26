import netmiko
from getpass import getpass
import datetime
import os

def ExtractHosts(): # Extract list of hosts from file
    with open('hosts.txt', 'r') as hostfile:
        hosts = hostfile.readlines()
    return hosts

def ExtractCommands(command_file): #
    with open('commands.txt', 'r') as cmdfile:
        commands = cmdfile.readlines()
    return commands

def WriteToFile(reply):
    with open(outfile, 'a') as f:
        f.write(reply)
        f.write('\n\n')

date = datetime.datetime.now() # Collect current date and time
username = input('Please enter an SSH username: ')
password = getpass()
hosts = ExtractHosts()
command_file = 'config_commands.txt'
outfile = 'output.txt'

print('The following devices will be accessed:\n')
for device in hosts:
    print(device.rstrip('\n'))
print()

# If/else block collects information of command source and privileges

ad_hoc_or_file = input('Are you making config changes from a file? (y/n): ')

if ad_hoc_or_file == 'n':
    enable_required = input('Does this command require enable mode? y/n : ')
    command = input('What command do you want to run?: ')
else:
     enable_required = 'y'

# Main loop cycles through devices with supplies variables and credentials to writes output to a file

for device in hosts:
    try:
        device = device.rstrip('\n')
        # Below line forms the SSH connection with supplied variables
        connection = netmiko.ConnectHandler(host=device, device_type='cisco_xe', username=username, password=password, secret=password)
        if enable_required.lower() == 'y': # Enters enable mode if requested
            connection.enable()
        if ad_hoc_or_file.lower() == 'n':
            print(f'{device} returned the following output:')
            print()
            reply = connection.send_command(command) # Runs ad-hoc command
            print(reply)
            WriteToFile(reply)
        if ad_hoc_or_file.lower() == 'y':
            print(f'{device} returned the following output:')
            print()
            reply = connection.send_config_from_file(command_file) # Pulls config from file and runs
            print(reply)
            WriteToFile(reply)
        connection.disconnect()
        print()
    # These two except clauses handle common errors
    except netmiko.ssh_exception.NetmikoTimeoutException:
        print(f'{device} could not be reached on port 22 - skipping to next device.\n')
        with open(outfile, 'a') as f:
            f.write(f'{device} could not be reached on port 22 - the device was skipped.\n\n')
        continue
    except UnicodeEncodeError:
        print(f'Output from {device} could not be encoded into UTF-8 format. Output could not be written to file.\n\n')
        with open(outfile, 'a') as f:
            f.write(f'Output from {device} could not be encoded into UTF-8 format. Output could not be written to file.\n\n')
        continue
# Two kinds of files are written afterwards based on command type
if ad_hoc_or_file == 'n':
    os.rename(outfile, command.replace(' ', '_') + f'_{date.month}-{date.day}-{date.year}-{date.hour}-{date.minute}.txt')
if ad_hoc_or_file == 'y':
    os.rename(outfile, f'config_changes_{date.month}-{date.day}-{date.year}-{date.hour}-{date.minute}.txt')

import netmiko
from getpass import getpass
import datetime
import os
import shutil

"""
Add error handling for missing/empty host/config files.

"""

def ExtractHosts(): # Extract list of hosts from file
    with open('hosts.txt', 'r') as hostfile:
        hosts = hostfile.readlines()
    return hosts

def ExtractCommands(): #
    with open('config_commands.txt', 'r') as cmdfile:
        commands = cmdfile.readlines()
    return commands

def WriteToFile(reply):
    with open(outfile, 'a') as f:
        f.write(reply + '\n\n')

# Global Variables
cwd = os.getcwd()
date = datetime.datetime.now() # Collect current date and time
hosts = ExtractHosts()
command_file = ExtractCommands()
outfile = 'output.txt'

print('The following devices will be accessed:\n')
for device in hosts:
    print(device.rstrip('\n'))
print()

# If/else blocks collect information of command source and privileges
while True:
    ad_hoc_or_file = input('Are you making config changes from a file? (y/n): ')
    if ad_hoc_or_file not in ('y', 'n'):
        print('Not a valid response\n')
        continue
    if ad_hoc_or_file == 'y':
        warning = input('\nPlease note - this will make config changes to \n\
the live running config, which can be VERY risky. \n\
Please write memory first. Are you sure you want to proceed? (y/n): ')
        if warning == 'y':
            break
        else:
            print('y not selected - exiting program')
            exit()
    else:
        break
# Asks about enable mode
if ad_hoc_or_file == 'n':
    while True:
        enable_required = input('Does this command require enable mode? y/n : ')
        if enable_required not in ('y', 'n'):
            print('Not a valid response\n')
            continue
        else:
            break
    command = input('What command do you want to run?: ')
else:
     enable_required = 'y'
print()

# Request SSH credentials
username = input('Please enter an SSH username: ')
password = getpass()

# Main loop cycles through devices with supplies variables and credentials to writes output to a file

for device in hosts:
    try:
        device = device.rstrip('\n')
        # Below line forms the SSH connection with supplied variables
        connection = netmiko.ConnectHandler(host=device, device_type='cisco_xe', username=username, password=password, secret=password)
        if enable_required.lower() == 'y': # Enters enable mode if requested
            connection.enable()
        if ad_hoc_or_file.lower() == 'n':
            reply = f'{device} returned the following output:\n\n' \
            + connection.send_command(command) # Runs ad-hoc command
            print(reply)
            WriteToFile(reply)
        if ad_hoc_or_file.lower() == 'y':
            reply = f'{device} returned the following output:\n\n' \
            + connection.send_config_from_file(command_file) # Pulls config from file and runs
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
    except netmiko.ssh_exception.NetmikoAuthenticationException:
        print('SSH Credentials are not valid - please check and try again.')
        exit()
# Create logdir if not existing already
if os.path.isdir('logs') == False:
    os.mkdir(cwd+'\\logs')
logdir = cwd+'\\logs\\'
# Remove output.txt if program failed to finish last time
if os.path.exists(logdir+'output.txt'):
    os.remove(logdir+'output.txt')
# Two kinds of files are written afterwards based on command type
if ad_hoc_or_file == 'n':
    shutil.move(outfile, logdir)
    os.chdir(logdir)
    # Name after command and remove illegal characters from file name
    new_file_name = command.replace('|', '')
    new_file_name = new_file_name.replace(' ', '_')
    print('New file created in logs/' + new_file_name + f'_{date.month}-{date.day}-{date.year}-{date.hour}-{date.minute}.txt')
    os.rename(outfile, new_file_name + f'_{date.month}-{date.day}-{date.year}-{date.hour}-{date.minute}.txt')
if ad_hoc_or_file == 'y':
    shutil.move(outfile, logdir)
    os.chdir(logdir)
    os.rename(outfile, f'config_changes_{date.month}-{date.day}-{date.year}-{date.hour}-{date.minute}.txt')

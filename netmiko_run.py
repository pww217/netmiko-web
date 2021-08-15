import netmiko
import os
import datetime
import shutil
from getpass import getpass
import logging

# Configure logging
logging.basicConfig(filename='run.log', level=logging.INFO)

# Function defs

def ExtractHosts(): # Extract list of hosts from file
    with open('hosts.txt', 'r') as hostfile:
        hosts = hostfile.readlines()
    logging.debug(f'Hosts are: {hosts}')
    return hosts

def ExtractCommands(): #
    with open('config_commands.txt', 'r') as cmdfile:
        commands = cmdfile.readlines()
    logging.debug(f'Found commands are: {commands}')
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

"""
Flow Logic

"""

# If/else loops collect information of command source and privileges
while True:
    use_input_file = input('Are you making config changes from a file? (y/n): ').lower()
    if use_input_file not in ('y', 'n'):
        print('Not a valid response\n')
        continue
    elif use_input_file == 'y':
        warning = input('\nPlease note - this will make config changes to \n\
the live running config, which can be VERY risky. \n\
Please write memory first. Are you sure you want to proceed? (y/n): ').lower()
        if warning == 'y':
            break
        else:
            print('y not selected - exiting program')
            exit()
    else:
        break

# Asks about enable mode privileges
if use_input_file == 'n':
    while True:
        enable_required = input('Does this command require enable mode? (y/n) : ').lower()
        if enable_required not in ('y', 'n'):
            print('Not a valid response\n')
            continue
        else:
            break
    command = input('What command do you want to run?: ')
else:
     enable_required = 'y'
print()

"""
Main program begins

"""

# Request SSH credentials
username = input('Please enter an SSH username: ')
password = getpass()

# Main loop cycles through devices with supplies variables and credentials to writes output to a file

for device in hosts:
    try:
        device = device.rstrip('\n')
        # Below line forms the SSH connection with supplied variables
        connection = netmiko.ConnectHandler(host=device, device_type='cisco_xe', username=username, password=password, secret=password)
        if enable_required == 'y': # Enters enable mode if requested
            connection.enable()
        if use_input_file == 'n':
            reply = f'{device} returned the following output:\n\n' \
            + connection.send_command(command) # Runs ad-hoc command
            print(reply)
            WriteToFile(reply)
        if use_input_file == 'y':
            reply = f'{device} returned the following output:\n\n' \
            + connection.send_config_from_file(command_file) # Pulls config from file and runs
            print(reply)
            WriteToFile(reply)
        connection.disconnect() # Graceful SSH terminate
        print()

    # These except clauses handle common errors
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
    os.mkdir(cwd+'\\logs') # Only works on Windows for now!
logdir = cwd+'\\logs\\'

# Clean up output.txt if program failed to finish last time
if os.path.exists(logdir+'output.txt'):
    os.remove(logdir+'output.txt')

# Two kinds of log files are written afterwards based on command type
if use_input_file == 'n':
    shutil.move(outfile, logdir)
    os.chdir(logdir)
    # Name file after running command and remove illegal characters from file name
    new_file_name = command.replace('|', '')
    new_file_name = new_file_name.replace(' ', '_')
    print('New file created in logs/' + new_file_name + f'_{date.month}-{date.day}-{date.year}-{date.hour}-{date.minute}.txt')
    os.rename(outfile, new_file_name + f'_{date.month}-{date.day}-{date.year}-{date.hour}-{date.minute}.txt')
else:
    shutil.move(outfile, logdir)
    os.chdir(logdir)
    os.rename(outfile, f'config_changes_{date.month}-{date.day}-{date.year}-{date.hour}-{date.minute}.txt')

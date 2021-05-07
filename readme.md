-- Netmiko Run ---  pww217, 2021

This program will allow you use run ad-hoc commands in user or enable mode on a Cisco 
IOS-XE device, as well as submit configuration changes from an input file directly.

--- How to Use ---
1. From Windows cmd line, powershell, or another shell, change directory (cd) until you reach the program's directory containing .py and dependent files
2. Edit host and cmd files to your liking, one command or host per line. Use template files as guides.
3. Run "python netmiko_run" or "python3 netmiko_run" depending on your python version and environmental variables
4. Choose one of the below modes:

--- Configuration Mode - merge commands from a file into running configuration ---

1. At the first prompt, select 'y' if making config-mode changes from the file config_commands.txt. Otherwise choose n to run a single, ad-hoc command.
   Note: 'conf t' and 'exit' do not need to be written in config_commands.txt - these are implied. 
2. Enter device credentials when prompted. These can be local, TACACS, ISE - anything the device will authenticate.
3. Output will be written to shell as well as a file with a timestamp to /logs in the working directory

--- Ad Hoc Mode - run a single command in user or enable mode ---

1. Specify whether enable mode is necessary
2. Write the command you want to run. Pipes '|' and other advanced operators are supported.
3. Enter device credentials when prompted. These can be local, TACACS, ISE - anything the device will authenticate.
4. Output will be written to shell as well as a file with a timestamp to /logs in the working directory
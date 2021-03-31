This program will allow you use run ad-hoc commands in user or enable mode on a Cisco IOS-XE device, as well as submit configuration changes from a file directly.

How to use:
1. From Windows cmd line, powershell, or another shell, change directory (cd) until you reach the program's directory containing .py and dependent files
2. Edit host and cmd files to your liking, one command or host per line. Use template files as guides.
3. Run "python netmiko_run" or "python3 netmiko_run" depending on your environmental variables
4. At the first prompt, select y if making config-mode changes from the file config_commands.txt. Note: 'conf t' and 'exit' do not need to be written in config_commands.txt - these are implied. Otherwise choose n to run a single, ad-hoc command.
5. (If selected ad-hoc) specify whether enable mode is necessary
6. (If selected ad-hoc) write the command you want to run. Pipes '|' and other advanced operators are allowed.
7. Output will be written to shell as well as a file with a timestamp to /logs in the working directory
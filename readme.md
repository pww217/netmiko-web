This program will allow you use run ad-hoc commands in user or enable mode on a Cisco IOS-XE device,
as well as submit configuration changes from a file directly.

How to use:
1. From Windows cmd line or another shell, change directly (cd) until you reach the program's directory containing .py and dependent files
2. Edit host and cmd files to your liking, one command or host per line.
3. Run "python netmiko_run" or "python3 netmiko_run" depending on your environmental variables
4. Enter credentials
5. Select whether you're running ad-hoc (single) commands or changing config from the file "commands.txt"
6. (If selected ad-hoc) specify whether enable mode is necessary
7. Output will be written to shell as well as a file with a timestamp
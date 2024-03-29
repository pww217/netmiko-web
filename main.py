from flask import Flask, request, render_template, redirect
import logging.config
import logging
from netmiko import ConnectHandler, NetmikoAuthenticationException, NetmikoTimeoutException
import os

"""
Flask-based Netmiko application for Cisco IOS and Linux
https://github.com/pww217
"""

# ~~~ Global Variables

# Working i/o files for each run (ideally would be dynamic or DB to allow multiple sessions)
OUTPUT_FILE = 'output.txt'
OUTPUT_HTML = 'output.html'
BACK_BUTTON = '<h4><a href="/">Return to Previous Page</h4></a>'

# ~~~ Logging Configuration

logging.config.dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    },
    'file': {
        'class': 'logging.handlers.RotatingFileHandler',
        'formatter': 'default',
        'filename': 'run.log',
        'mode': 'a',
        'maxBytes': 10485760,
        'backupCount': 5,
    }},
    'root': {
        'level': 'DEBUG',
        'handlers': ['wsgi', 'file']
    }
})

# ~~~ Function Definitions

# I/O unitaskers
def write_hosts(input):
    with open('hosts.txt', 'w') as hostfile:
        hostfile.write(input)
        logging.debug('Wrote hosts to file')

def retrieve_hosts():
    if os.path.exists('hosts.txt') == False:
        os.mknod('hosts.txt')
        logging.debug('Creating new hosts.txt file')
    with open('hosts.txt', 'r') as hostfile:
        hosts = hostfile.readlines()
    return hosts

def write_output_file(cmd_reply):
    with open(OUTPUT_FILE, 'a') as file:
        file.write('<pre>' + cmd_reply + '</pre>')
    logging.debug('Wrote command output to output.txt')
    return file

def convert_to_html():
    with open(OUTPUT_FILE, 'r') as file:
        html_string = file.read()
    logging.debug('Converted output.txt to output.html')
    return html_string

def clean_temp_files():
    try:
        os.remove(OUTPUT_FILE)
        os.remove(OUTPUT_HTML)
    except FileNotFoundError:
        pass

def enable_on(os_type):
    if os_type == 'cisco_xe' and request.form.get('enable') == 'on':
        enable_mode = 'on'
        return enable_mode
    else:
        return 'off'

def gather_input(os_type):
    hosts = retrieve_hosts() # From host.txt
    logging.debug(f'Hosts registered as '+ format_file('hosts.txt'))
    # These 4 come from the HTTP POST
    user = request.form.get('uname')
    password = request.form.get('passwd')
    command = request.form.get('cmd')
    if os_type == 'cisco_xe' and request.form.get('enable') == 'on' \
    or os_type == 'cisco_xe_config':
        enable_mode = 'on'
    else:
        enable_mode = 'off'
    logging.info(f'ostype = {os_type}, user = {user}; command = {command}; ' \
        f'enable_mode = {enable_mode}')
    return hosts, user, password, command, enable_mode

# Main Netmiko Loop with two common exceptions and a catch-all
def run_command(hosts, os_type, user, password, command, enable_mode='None'):
    # Return link generated at the top of each return
    write_output_file(f'<h4><a href="/{os_type}/">Return to Previous Page</a></h4>')
    for device in hosts: # hosts is a list for easy iteration
        try:
            device = device.rstrip('\n') # Strip newline from host
            if os_type == 'cisco_xe_config': # Check for type: config mode
                with open('config.txt', 'w') as config_file: # This method requires file object
                    config_file.write(command)
                with open('config.txt', 'r') as config_file:
                    logging.info(f'config.txt contains {config_file.read()}')
                os_type = 'cisco_xe' # Change back to valid OS type for below method
                connection = ConnectHandler(host=device, device_type=os_type, \
                    username=user, password=password, secret=password) # Create connection handler
                reply = f'<h3>{device} returned the following output:</h3>'+ \
                connection.send_config_from_file(config_file='config.txt') # Run list of commands in config mode
            else: # Used for all non-config changing ad-hoc commands
                connection = ConnectHandler(host=device, device_type=os_type, \
                    username=user, password=password, secret=password) # Create connection handler   
                if enable_mode == 'on': # Check for enable mode and activate
                    connection.enable()       
                reply = f'<h3>{device} returned the following output:</h3>'+ \
                connection.send_command(command, expect_string="[\\ ~\\#]") # Runs a single command      
            write_output_file(reply)
            logging.info(f'Wrote {device} output to file')
            connection.disconnect() # Graceful SSH disconnect
        # Common exceptions and a catch-all
        except NetmikoTimeoutException:
            message = f'<h3>{device} could not be reached on port 22 - ' \
                                        'skipping to next device.</h3>'
            logging.warning(message.replace('</h3>', '').replace('<h3>', ''))
            write_output_file(message)
        except NetmikoAuthenticationException:
            message = f'<h3>{device} had invalid credentials</h3>'
            logging.warning(message.replace('</h3>', '').replace('<h3>', ''))
            write_output_file(message)
        except UnicodeEncodeError:
            message = f'<h3>Output from {device} could not be encoded into UTF-8 format.' \
                            'Output could not be written to file.</h3>'
            logging.error(message.replace('</h3>', '').replace('<h3>', ''))
            write_output_file(message)
        except ValueError:
            message = f'<h3>Unrecognized shell prompt from {device}; usually caused by using a non-standard or customized shell.</h3>'
            logging.error(message.replace('</h3>', '').replace('<h3>', ''))
            write_output_file(message)

# Handles main index page and gathers host and OS information
def handle_root_url():
    selection = None
    hosts = retrieve_hosts() # Use existing hosts in hosts.txt if nothing entered
    if request.method == "POST":
        logging.debug('HTTP method = POST')
        if request.form.get('selection'): # Checks for radio button OS choice
            selection = request.form.get('selection')
        logging.debug(f'{selection} option selected')
        if request.form.get('hosts'): # Checks for any new host entries
            hosts = request.form.get('hosts')
            write_hosts(hosts) # to hosts.txt
        if selection and hosts: # If both inputs are populated by POST or file
            # Redirect to appropriate URL
            if selection == 'cisco_xe':
                return redirect('cisco_xe')
            else:
                return redirect('linux')
        else: # Handles missing required information
            if not selection and not hosts:
                return render_template('index.html') + '<p>Please selection an OS and add at least one host</p>'
            elif not selection:
                return render_template('index.html') + '<p>Please make an OS selection</p>'
            else:
                return render_template('index.html') + '<p>Please add at least one host</p>'
    else: # Redirects if no input
        logging.debug('HTTP method = GET')
        return render_template('index.html')

# Handles non-index URLs; gathers info and returns a template based on POST input
def handle_sub_url(os_type, template):
    if request.method == "POST":
        logging.debug('HTTP method = POST')
        hosts, user, password, command, enable_mode = gather_input(os_type)
        if user and password and command:
            #Run main loop
            run_command(hosts, os_type, user, password, command, enable_mode)
            #Convert UTF-8 to HTML and store
            results = convert_to_html()
            clean_temp_files() # Clean any leftover temp files
            return results
        else:
            return render_template(template) + '<br><br /><b>Error:</b> Please enter all required fields'
    else: # Otherwise display page template
        logging.debug('HTTP method = GET')
        return render_template(template)

def format_file(filename):
    with open(filename, 'r') as f:
        contents = '<pre>' + f.read() + '</pre>'
    return contents

# ~~~ Instantiate the Webpage Object

app = Flask(__name__)

# ~~~ URL directory decorators

@app.route('/', methods=['GET', 'POST']) # Root directory
def root_dir():
    return handle_root_url()


@app.route('/cisco_xe/', methods = ['GET', 'POST']) # Cisco Directory
def cisco_xe_dir():
    return handle_sub_url('cisco_xe', 'cisco_xe.html')


@app.route('/cisco_xe_config/', methods = ['GET', 'POST'])
def cisco_xe_config_dir():
    return handle_sub_url('cisco_xe_config', 'cisco_xe_config.html')


@app.route('/linux/', methods = ['GET', 'POST']) # Linux Directory
def linux_dir():
    return handle_sub_url('linux', 'linux.html')


@app.route('/hosts/', methods = ['GET']) # Linux Directory
def hosts_dir():
    if retrieve_hosts():
        return f'{BACK_BUTTON}<p><b>Current Hosts:</p></b>' + format_file('hosts.txt')
    else:
        return f'{BACK_BUTTON} </a>No Hosts Found'


@app.route('/log/', methods = ['GET']) # run.log output
def log_dir():
    with open('run.log', 'r') as l:
        if os.path.isfile('run.log'):
            return f'{BACK_BUTTON}' + format_file('run.log')


# ~~~ Run the web server from local private IP on TCP/5000 with debugging
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
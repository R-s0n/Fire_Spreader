import requests, sys, subprocess, getopt, json

full_cmd_arguments = sys.argv
argument_list = full_cmd_arguments[1:]
short_options = "d:"
long_options = ["domain="]

try:
    arguments, values = getopt.getopt(argument_list, short_options, long_options)
except:
    sys.exit(2)

for current_argument, current_value in arguments:
    if current_argument in ("-d", "--domain"):
        fqdn = current_value

r = requests.post('http://10.0.0.211:8000/api/auto', data={'fqdn':fqdn})
thisFqdn = r.json()

server_data_arr = thisFqdn['recon']['subdomains']['masscan']
live_server_arr = []

for target in server_data_arr:
    connect = subprocess.run([f"echo {target} | ~/go/bin/httprobe -t 50000"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, shell=True)
    temp_arr = connect.stdout.split("\n")
    for each in temp_arr:   
        if len(each) > 5:
            print(f"[+] Found live webserver: {each}")
            live_server_arr.append(each)

thisFqdn['recon']['subdomains']['masscanLive'] = live_server_arr
r = requests.post('http://10.0.0.211:8000/api/auto/update', json=thisFqdn, headers={'Content-type':'application/json'})

if r.status_code == 200:
    print("[+] Wind.py completed successfully!")
else:
    print("[!] Wind.py did NOT complete successfully!")
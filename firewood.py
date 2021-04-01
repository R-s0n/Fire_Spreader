# Long scan using dnmasscan

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

subdomainArr = thisFqdn['recon']['subdomains']['consolidated']

initial_check = subprocess.run(["ls ~/Tools/dnmasscan"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
if initial_check.returncode == 0:
    print("[+] Dnmasscan is installed")
else :
    print("[!] Dnmasscan is NOT installed -- Installing now...")
    cloning = subprocess.run(["cd ~/Tools; git clone https://github.com/rastating/dnmasscan.git;"], stdout=subprocess.DEVNULL, shell=True)
    print("[+] Dnmasscan was successfully installed")

initial_check_two = subprocess.run(["ls ~/Tools/masscan"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
if initial_check_two.returncode == 0:
    print("[+] Masscan is installed")
else :
    print("[!] Masscan is NOT installed -- Installing now...")
    cloning = subprocess.run(["cd ~/Tools; sudo apt-get --assume-yes install git make gcc; git clone https://github.com/robertdavidgraham/masscan; cd masscan; make; make install;"], stdout=subprocess.DEVNULL, shell=True)
    print("[+] Masscan was successfully installed")


consolidatedStr = ""
for subdomain in subdomainArr:
    if subdomain[0] == ".":
        modified_subdomain = subdomain[1:]
        consolidatedStr += f"{modified_subdomain}\n"
    else:
        consolidatedStr += f"{subdomain}\n"
f = open("/tmp/dnmasscan.tmp", "w")
f.write(consolidatedStr)
f.close()
dnmasscan_results = subprocess.run(["cd ~/Tools/dnmasscan; sudo ./dnmasscan /tmp/dnmasscan.tmp /tmp/dns.log -p1-65535 -oJ /tmp/masscan.json --rate=500"], shell=True)
subprocess.run(["rm /tmp/dnmasscan.tmp"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
f = open("/tmp/masscan.json", "r")
masscan_data = json.load(f)
thisFqdn['recon']['subdomains']['masscan'] = masscan_data


r = requests.post('http://10.0.0.211:8000/api/auto/update', json=thisFqdn, headers={'Content-type':'application/json'})
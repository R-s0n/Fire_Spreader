import requests, sys, subprocess, getopt, json
from datetime import datetime

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

go_check = subprocess.run(["go version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
if go_check.returncode == 0:
    print("[+] Go is installed")
else :
    print("[!] Go is NOT installed -- Installing now...")
    cloning = subprocess.run(["sudo apt-get install -y golang-go; apt-get install -y gccgo-go; mkdir ~/go;"], stdout=subprocess.DEVNULL, shell=True)
    print("[+] Go was successfully installed")

try:
    httprobe_check = subprocess.run(["~/go/bin/httprobe -h"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
    if httprobe_check.returncode == 0:
        print("[+] Httprobe is already installed")
    else :
        print("[!] Httprobe is NOT already installed -- Installing now...")
        cloning = subprocess.run(["go get -u github.com/tomnomnom/httprobe"], stdout=subprocess.DEVNULL, shell=True)
        print("[+] Httprobe successfully installed!")
    print(f"[-] Running Httprobe against {fqdn}...")
    subdomainStr = ""
    for subdomain in subdomainArr:
        subdomainStr += f"{subdomain}\n"
    f = open("/tmp/consolidated_list.tmp", "w")
    f.write(subdomainStr)
    f.close()
    httprobe_results = subprocess.run([f"cat /tmp/consolidated_list.tmp | ~/go/bin/httprobe -t 20000 -p http:8080 -p http:8000 -p http:8008 -p https:8443 -p https:44300 -p https:44301"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, shell=True)
    httprobe = httprobe_results.stdout.split("\n")
    previous_httprobe = thisFqdn['recon']['subdomains']['httprobe']
    httprobeAdded = []
    httprobeRemoved = []
    for subdomain in httprobe:
        if subdomain not in previous_httprobe:
            httprobeAdded.append(subdomain)
    for subdomain in previous_httprobe:
        if subdomain not in httprobe:
            httprobeRemoved.append(subdomain)
    thisFqdn['recon']['subdomains']['httprobe'] = httprobe
    thisFqdn['recon']['subdomains']['httprobeAdded'] = httprobeAdded
    thisFqdn['recon']['subdomains']['httprobeRemoved'] = httprobeRemoved
    print("[+] Httprobe completed successfully!")
except:
    print("[!] Httprobe module did NOT complete successfully -- skipping...")

subprocess.run(["rm /tmp/consolidated_list.tmp"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
# Send new fqdn object
r = requests.post('http://10.0.0.211:8000/api/auto/update', json=thisFqdn, headers={'Content-type':'application/json'})

directory_check = subprocess.run([f"ls ~/Reports"], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, shell=True)
if directory_check.returncode == 0:
    print("[+] Identified Reports directory")
else:
    print("[!] Could not locate Reports directory -- Creating now...")
    cloning = subprocess.run([f"mkdir ~/Reports"], stdout=subprocess.DEVNULL, shell=True)
    print("[+] Reports directory successfully created")

eyewitness_check = httprobe_check = subprocess.run(["ls ~/Tools/EyeWitness"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
if httprobe_check.returncode == 0:
    print("[+] EyeWitness is already installed")
else :
    print("[!] EyeWitness is NOT already installed -- Installing now...")
    cloning = subprocess.run(["cd ~/Tools; git clone https://github.com/FortyNorthSecurity/EyeWitness.git;  cd EyeWitness/Python/setup/;  sudo ./setup.sh"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
    print("[+] EyeWitness successfully installed!")
httprobe_string = ""
for subdomain in httprobe:
    httprobe_string += f"{subdomain}\n"
f = open("/tmp/httprobe_results.tmp", "w")
f.write(httprobe_string)
f.close()
now = datetime.now().strftime("%d-%m-%y")
print(f"[-] Running EyeWitness report against {fqdn} httprobe results...")
subprocess.run([f"cd ~/Tools/EyeWitness/Python; ./EyeWitness.py -f /tmp/httprobe_results.tmp -d ~/Reports/EyeWitness_{now} --no-prompt --jitter 5 --timeout 10"], shell=True)
print(f"[+] EyeWitness report complete!")
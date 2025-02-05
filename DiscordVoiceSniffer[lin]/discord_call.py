import os
import subprocess
import re
import time
from collections import defaultdict
import colorama
from colorama import Fore


if os.geteuid() != 0:
    print("Erreur : ce script doit être exécuté en tant que root.")
    exit(1)


def is_installed(command):
    return subprocess.call(['which', command], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0

if not is_installed("tcpdump"):
    print("tcpdump n'est pas installé. Installation en cours...")
    subprocess.run(["apt", "update"])
    subprocess.run(["apt", "install", "-y", "tcpdump"])


def get_interface():
    result = subprocess.run(["ip", "route"], stdout=subprocess.PIPE, text=True)
    match = re.search(r'default.*? dev (\S+)', result.stdout)
    return match.group(1) if match else None

interface = get_interface()
if not interface:
    print("Impossible de détecter l'interface réseau.")
    exit(1)

# Banner ASCII art
banner = r"""
         _nnnn_                      
        dGGGGMMb     ,"""""""""""""""""""""""""
       @p~qp~~qMb    | Discord Ecoute en Cours |
       M|@||@) M|   _;.........................'      
       @,----.JM| -'
      JS^\\__/  qKL          
     dZP         qKb        .
     dZP        qKRb
    dZP          qKKb
   fZP            SMMb
   HZM            MMMM
   FqM            MMMM
 __| ".        |\\dS"qML
 |    `.       | `' \\Zq
_)      \\.___.,|     .'
\\____   )MMMMMM|   .'
     `-'       `--' hjm
"""

print(f"{Fore.GREEN}{banner}{Fore.RESET}")

resolved_domains = defaultdict(str)


def resolve_domain(domain):
    result = subprocess.run(["dig", "+short", domain], stdout=subprocess.PIPE, text=True)
    for line in result.stdout.splitlines():
        if re.match(r'^\d+\.\d+\.\d+\.\d+$', line):
            return line
    return None


try:
    process = subprocess.Popen(
        ["tcpdump", "-i", interface, "udp port 53", "-n", "-s", "0", "-l"],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True
    )
    for line in iter(process.stdout.readline, ''):
        match = re.search(r'(?<=A\? )[^\s]+\.discord\.media', line)
        if match:
            domain = match.group(0)
            if domain not in resolved_domains:
                ip = resolve_domain(domain)
                if ip:
                    print(f"{domain:35} : {ip}")
                    resolved_domains[domain] = ip
        time.sleep(1)
except KeyboardInterrupt:
    print("\nArrêt du script.")
    process.terminate()

import os
import time
from scapy.all import sniff, IP, UDP
from collections import defaultdict
import random
import colorama
from colorama import Fore


def is_admin():
    try:
        return os.getuid() == 0
    except AttributeError:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin() != 0

if not is_admin():
    print("Erreur : ce script doit être exécuté en tant qu'administrateur.")
    exit(1)


banner = r"""
         _nnnn_                      
        dGGGGMMb     ,"""""""""""""""""""""""""
       @p~qp~~qMb    | Discord Écoute en Cours |
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


connection_cache = defaultdict(float)
CACHE_EXPIRATION = 60  


TARGET_IPS = ["192.168.1.1"] # Vos IPv4/IPv6
MASKED_IP = "*.*.*.*"

def mask_ip(ip):
    """
    Masque une IP si elle figure dans la liste des IPs à flouter.
    """
    return MASKED_IP if ip in TARGET_IPS else ip

def detect_voice_connection(packet):
    """
    Callback pour traiter les paquets UDP Discord vocaux.
    """
    if packet.haslayer(IP) and packet.haslayer(UDP):
        ip_src = packet[IP].src
        ip_dst = packet[IP].dst
        port_src = packet[UDP].sport
        port_dst = packet[UDP].dport

        
        ip_src = mask_ip(ip_src)
        ip_dst = mask_ip(ip_dst)

        
        connection_key = f"{ip_src}:{port_src} → {ip_dst}:{port_dst}"

       
        current_time = time.time()
        if current_time - connection_cache[connection_key] > CACHE_EXPIRATION:
           
            connection_cache[connection_key] = current_time
            
            
            print(f"Nouvelle connexion vocale détectée :")
            print(f"IP Source: {Fore.CYAN}{ip_src}:{port_src}{Fore.RESET} → IP Destination: {Fore.CYAN}{ip_dst}:{port_dst}{Fore.RESET}")


try:
    print("Écoute du trafic UDP Discord... Parle dans un canal vocal pour voir les connexions réseau :")
    sniff(filter="udp", prn=detect_voice_connection, store=0)
except KeyboardInterrupt:
    print("\nArrêt du script.")
except PermissionError:
    print("Erreur : ce script doit être exécuté en tant qu'administrateur.")

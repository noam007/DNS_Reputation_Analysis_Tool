# PCAP מה DNS מחלץ

import time
import signal
from scapy.all import PcapReader, DNS, DNSQR

class TrafficReplayManager:
    def __init__(self, file_path):
        self.file_path = file_path
        self.domains = []
        self.packets_sent = 0
        self.domains_processed = 0
        self.errors = 0
        self.is_running = True
        self.cache = {}

    def extract_domains(self):
        try:
            for pkt in PcapReader(self.file_path):
                if not self.is_running:
                    print("Stopping PCAP processing...")
                    break

                self.packets_sent += 1

                if pkt.haslayer(DNS) and pkt[DNS].qd:
                    try:
                        domain = pkt[DNSQR].qname.decode().rstrip(".")
                        self.domains.append(domain)
                        self.domains_processed += 1
                        print(f"Domain found: {domain}")
                    except Exception:
                        self.errors += 1

                if self.packets_sent % 50 == 0:
                    print(f"[Live Stats] Packets: {self.packets_sent}, Domains: {self.domains_processed}, Errors: {self.errors}")

        except FileNotFoundError:
            print(f"File not found: {self.file_path}")
        except Exception as e:
            print(f"Error reading PCAP: {e}")


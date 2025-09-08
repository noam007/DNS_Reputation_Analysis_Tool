# Extracts DNS domains from PCAP

from threading import Event
from scapy.all import PcapReader, DNS, DNSQR


class TrafficReplayManager:
    def __init__(self, file_path):
        """
        Initializes the TrafficReplayManager with a PCAP file path.
        Sets up tracking for domains, packets, errors, and a stop event.
        """
        self.file_path = file_path
        self.domains = []
        self.packets_sent = 0
        self.domains_processed = 0
        self.errors = 0
        self.stop_event = Event()

    def extract_domains(self):
        """
        Reads packets from the given PCAP file and extracts DNS query domains.
        - Stops gracefully if stop_event is set.
        - Increments counters for packets, domains, and errors.
        - Prints live statistics every 50 packets.
        - Handles file not found and other reading errors.
        """
        try:
            for pkt in PcapReader(self.file_path):
                if self.stop_event.is_set():
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

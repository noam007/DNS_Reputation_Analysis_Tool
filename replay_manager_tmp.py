import time
import signal
from scapy.all import PcapReader, DNS, DNSQR
# from reputation_engine import AsyncReputationClient

class TrafficReplayManager:
    def __init__(self, file_path):
        self.file_path = file_path
        self.is_running = False
        self.start_time = None
        self.packets_sent = 0
        self.errors = 0
        self.domains_processed = 0

    def _process_pcap(self):
        """Internal method to process the PCAP file and send domains."""
        try:
            reader = PcapReader(self.file_path)

            for packet in reader:
                # Check the state of self.is_running in each iteration
                if not self.is_running:
                    print("\nReplay stopped gracefully.")
                    break

                self.packets_sent += 1

                if packet.haslayer(DNS) and packet.getlayer(DNS).qd is not None:
                    dns_name = packet[DNSQR].qname.decode()
                    self.domains_processed += 1
                    # Pass the domain to the reputation engine here
                    print(f"Domain query: {dns_name}")

        except FileNotFoundError:
            self.errors += 1
            print(f"Error: File '{self.file_path}' not found.")

        except Exception as e:
            self.errors += 1
            print(f"An unexpected error occurred: {e}")

        finally:
            self.stop()

    def start(self):
        """Starts the traffic replay process."""
        self.is_running = True
        self.start_time = time.time()
        self._process_pcap()

    def stop(self):
        """Stops the process and prints final stats."""
        if not self.is_running:
            return

        self.is_running = False
        total_time = time.time() - self.start_time
        qps = self.domains_processed / total_time if total_time > 0 else 0

        print("\n--- Final Statistics ---")
        print(f"Total runtime: {total_time:.2f} seconds")
        print(f"Packets processed: {self.packets_sent}")
        print(f"Domains processed: {self.domains_processed}")
        print(f"Errors encountered: {self.errors}")
        print(f"Query rate (QPS): {qps:.2f}")

    def graceful_shutdown(self, signum, frame):
        """Handles graceful shutdown on Ctrl+C."""
        print(f"\nReceived signal: {signum}")
        print("Exiting gracefully...")
        self.is_running = False


if __name__ == "__main__":
    file_path = "big_example.pcap"
    manager = TrafficReplayManager(file_path)

    # Attach the signal handler to Ctrl+C
    signal.signal(signal.SIGINT, manager.graceful_shutdown)

    print("Press Ctrl+C to trigger the signal handler.")
    manager.start()

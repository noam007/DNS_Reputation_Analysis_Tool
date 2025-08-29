import time
import signal
import asyncio
import aiohttp
from scapy.all import PcapReader, DNS, DNSQR
from reputation_engine import Reputation

class TrafficReplayManager:
    def __init__(self, file_path):
        self.file_path = file_path
        self.is_running = False
        self.start_time = None
        self.packets_sent = 0
        self.errors = 0
        self.domains_processed = 0
        self.domains = []  # collect domains here

    def _process_pcap(self):
        """Extract domains from PCAP file instead of calling Reputation directly."""
        try:
            reader = PcapReader(self.file_path)

            for packet in reader:
                if not self.is_running:
                    print("\nReplay stopped gracefully.")
                    break

                self.packets_sent += 1

                if packet.haslayer(DNS) and packet.getlayer(DNS).qd is not None:
                    dns_name = packet[DNSQR].qname.decode().rstrip(".")
                    self.domains_processed += 1
                    print(f"Domain query found: {dns_name}")
                    self.domains.append(dns_name)

        except FileNotFoundError:
            self.errors += 1
            print(f"Error: File '{self.file_path}' not found.")

        except Exception as e:
            self.errors += 1
            print(f"An unexpected error occurred: {e}")

        finally:
            self.stop()

    async def _query_reputation_bulk(self):
        """Send all collected domains to VirusTotal concurrently."""
        async with aiohttp.ClientSession() as session:
            tasks = [Reputation(session, d) for d in self.domains]
            results = await asyncio.gather(*tasks)

            print("\n--- Reputation Results ---")
            for res in results:
                print(res)

    def start(self):
        """Starts the traffic replay process."""
        self.is_running = True
        self.start_time = time.time()
        self._process_pcap()

        # After extracting domains, run async reputation lookups
        asyncio.run(self._query_reputation_bulk())

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
    file_path = "pcap_mid.pcap"
    manager = TrafficReplayManager(file_path)

    # Attach the signal handler to Ctrl+C
    signal.signal(signal.SIGINT, manager.graceful_shutdown)

    print("Press Ctrl+C to trigger the signal handler.")
    manager.start()


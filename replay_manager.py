from scapy.all import rdpcap, DNS , DNSQR
import time
import signal


class TrafficReplayManager:

    def __init__(self, income_file):
        self.incoming_file = income_file
        self.is_running = True

    def start(self):
        self.start_time = time.time()
        self.parse_pcap()

    def stop(self):
        self.end_time = time.time()
        self.parse_pcap()


    def parse_pcap(self):
        while self.is_running:
            dns_packets = []
            try:
                packets = rdpcap(income_file) # קריאת החבילות מהקובץ

                for packet in packets:    # מעבר על כל החבילות
                    time.sleep(0.1)
                    if packet.haslayer(DNS) and packet.getlayer(DNS).qd is not None:  # בדיקה אם קיימת שכבת DNS
                        DNS_name = packet[DNSQR].qname.decode()  # המרה מ-bytes ל-string
                        print("Domain query:", DNS_name ,"\n")
                        dns_packets.append(packet)
                return dns_packets

            except KeyboardInterrupt:
                # Handle CTRL+C gracefully
                self.is_running = False
                print("\nCTRL+C detected! Cleaning up...")
                # Perform any cleanup actions here
                return []

            except Exception as e:
                print(f"שגיאה בקריאת הקובץ: {e}")
                self.is_running = False
                return []



            # finally:
            #     print("Program has exited gracefully.")
            #     return []

        return None


# Example usage
if __name__ == "__main__":
    income_file = "example.pcap"
    manager = TrafficReplayManager(income_file)

    parsed_packets = manager.parse_pcap()
    print(f"נמצאו {len(parsed_packets)} חבילות DNS.")


# =============================
# DNS Traffic Reputation Tool
# =============================

import asyncio
import signal
import time
import aiohttp
from scapy.all import PcapReader, DNS, DNSQR
from reputation_engine import Reputation  # פונקציה אסינכרונית לבדיקת מוניטין

# =============================
# TrafficReplayManager Class
# =============================
class TrafficReplayManager:
    def __init__(self, file_path):
        # -------------------------
        # Initialization
        # -------------------------
        self.file_path = file_path
        self.domains = []
        self.packets_sent = 0
        self.domains_processed = 0
        self.errors = 0
        self.is_running = True            # דגל לעצירה עדינה
        self.cache = {}                   # Cache בסיסי: דומיין -> תוצאה

    # =============================
    # Extract DNS Domains from PCAP
    # =============================
    def extract_domains(self):
        """
        קריאת קובץ PCAP וחילוץ דומיינים מתוך בקשות DNS
        - בדיקה של דגל is_running לעצירה בזמן אמת
        - מעקב סטטיסטיקות בזמן הריצה (כל 50 חבילות)
        """
        try:
            for pkt in PcapReader(self.file_path):
                if not self.is_running:       # עצירה עדינה
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

                # מעקב בזמן אמת כל 50 חבילות
                if self.packets_sent % 50 == 0:
                    print(f"[Live Stats] Packets: {self.packets_sent}, Domains: {self.domains_processed}, Errors: {self.errors}")

        except FileNotFoundError:
            print(f"File not found: {self.file_path}")
        except Exception as e:
            print(f"Error reading PCAP: {e}")

    # =============================
    # Query Single Domain with Timeout + Retry + Cache
    # =============================
    async def query_domain_with_retry(self, session, domain, retries=3, timeout=10):
        """
        קריאה אסינכרונית למודול Reputation עם:
        - Timeout לכל שאילתה
        - Retry במקרה של כישלון
        - Cache בסיסי לשמירה על תוצאות חוזרות
        """
        # בדיקה אם הדומיין כבר קיים ב-cache
        if domain in self.cache:
            print(f"[Cache] {domain} -> {self.cache[domain]}")
            return self.cache[domain]

        attempt = 0
        while attempt < retries:
            try:
                # Timeout לכל שאילתה
                result = await asyncio.wait_for(Reputation(session, domain), timeout=timeout)
                self.cache[domain] = result   # שמירה ב-cache
                return result
            except Exception as e:
                attempt += 1
                print(f"[Retry {attempt}] Domain {domain} failed: {e}")
                if attempt >= retries:
                    result = {"domain": domain, "error": str(e)}
                    self.cache[domain] = result
                    return result

    # =============================
    # Query All Domains Asynchronously
    # =============================
    async def query_domains(self):
        """
        שאילת מוניטין לכל הדומיינים שנמצאו במקביל
        - משתמש ב-query_domain_with_retry
        - מבצע gather לכל המשימות
        """
        async with aiohttp.ClientSession() as session:
            tasks = [self.query_domain_with_retry(session, d) for d in self.domains]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            print("\n--- Reputation Results ---")
            for r in results:
                print(r if not isinstance(r, Exception) else f"Error: {r}")

    # =============================
    # Graceful Shutdown Handler
    # =============================
    def graceful_shutdown(self, signum, frame):
        """
        עצירה עדינה בעת לחיצה על Ctrl+C
        - משנה את הדגל is_running
        - הלולאה extract_domains תעצור בזמן אמת
        """
        print(f"\nCtrl+C detected (signal {signum})! Stopping gracefully...")
        self.is_running = False

    # =============================
    # Run Full Process
    # =============================
    def run(self):
        """
        הרצת התהליך המלא:
        1. Start - חילוץ דומיינים
        2. Monitor - סטטוס חי בזמן הריצה
        3. Query domains עם Timeout + Retry + Cache
        4. Stop - הדפסת סטטיסטיקות סופיות
        """
        start_time = time.time()

        print("Starting PCAP processing...")
        self.extract_domains()                       # חילוץ דומיינים

        print("Starting Reputation queries...")
        asyncio.run(self.query_domains())            # שאילת מוניטין אסינכרונית

        # חישוב סטטיסטיקות סופיות
        total_time = time.time() - start_time
        qps = self.domains_processed / total_time if total_time > 0 else 0

        print("\n--- Final Statistics ---")
        print(f"Packets processed: {self.packets_sent}")
        print(f"Domains processed: {self.domains_processed}")
        print(f"Errors encountered: {self.errors}")
        print(f"Query rate (QPS): {qps:.2f}")

# =============================
# Main Execution
# =============================
if __name__ == "__main__":
    file_path = "pcap_single.pcap"
    manager = TrafficReplayManager(file_path)

    # התקנת Handler לעצירת Ctrl+C
    signal.signal(signal.SIGINT, manager.graceful_shutdown)
    print("Press Ctrl+C to stop the process gracefully.\n")

    # הרצת התהליך
    manager.run()

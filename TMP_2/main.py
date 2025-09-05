import asyncio
import time
import signal
from traffic_manager import TrafficReplayManager
from async_queries import AsyncQueryManager
from utils import graceful_shutdown ,final_statistics
from reputation_engine import save_results_json

if __name__ == "__main__":
    file_path = "pcap_single.pcap"
    manager = TrafficReplayManager(file_path)

    # התקנת Ctrl+C Handler
    signal.signal(signal.SIGINT, lambda s, f: graceful_shutdown(manager, s, f))
    print("Press Ctrl+C to stop the process gracefully.\n")

    # 1. חילוץ דומיינים
    start_time = time.time()
    print("Starting PCAP processing...")
    manager.extract_domains()

    # 2. שאילת מוניטין
    print("Starting Reputation queries...")
    query_manager = AsyncQueryManager(manager.cache)
    asyncio.run(query_manager.query_domains(manager.domains))

    # 3. סטטיסטיקות סופיות
    total_time = time.time() - start_time
    qps = manager.domains_processed / total_time if total_time > 0 else 0

    final_statistics(manager,qps)
    save_results_json()
import asyncio
import time
import signal
from traffic_manager import TrafficReplayManager
from async_queries import AsyncQueryManager
from utils import graceful_shutdown, final_statistics, save_results_csv



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
    query_manager = AsyncQueryManager(manager.cache, rps=5)    # 5 requests per second
    asyncio.run(query_manager.query_domains(manager.domains))
    results = asyncio.run(query_manager.query_domains(manager.domains))

    # 3. סטטיסטיקות סופיות
    total_time = time.time() - start_time
    final_statistics(manager, results, total_time)
    save_results_csv(results, csv_file="results.csv", source_file=file_path)
import sys
import asyncio
import time
import signal
from traffic_manager import TrafficReplayManager
from async_queries import AsyncQueryManager
from utils import graceful_shutdown, final_statistics, save_results_csv



if __name__ == "__main__":
    file_path = "pcap_big.pcap"
    manager = TrafficReplayManager(file_path)
    query_manager = AsyncQueryManager(rps=5)  # 5 requests per second

    # Install Ctrl+C Handler
    signal.signal(signal.SIGINT, lambda s, f: graceful_shutdown(manager, query_manager, s, f))
    print("Press Ctrl+C to stop the process gracefully.\n")

    # 1. Extract domains
    start_time = time.time()
    print("Starting PCAP processing...")
    manager.extract_domains()

    # 2. Reputation queries
    print("Starting Reputation queries...")

    try:
        asyncio.run(query_manager.query_domains(manager.domains))
        results = asyncio.run(query_manager.query_domains(manager.domains))
    except asyncio.exceptions.CancelledError:
        # TDOD add prints
        sys.exit(1)

    # 3. Final statistics
    total_time = time.time() - start_time
    final_statistics(manager, results, total_time)
    save_results_csv(results, csv_file="results.csv", source_file=file_path)

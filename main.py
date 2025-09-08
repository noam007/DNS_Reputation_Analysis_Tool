import sys
import asyncio
import time
import signal
from traffic_manager import TrafficReplayManager
from async_queries import AsyncQueryManager
from utils import graceful_shutdown, final_statistics, save_results_csv


if __name__ == "__main__":
    """
    Main script for processing a PCAP file:
    1. Loads PCAP and extracts DNS domains.
    2. Queries reputation services asynchronously for each domain.
    3. Handles graceful shutdown on Ctrl+C.
    4. Prints final statistics and saves results to CSV.
    """

    # Prompt the user to enter a PCAP file path.
    # If no input is given, the default file is "pcap_big.pcap".
    file_path = input("Enter the path to the pcap file (empty is default): ").strip()

    if file_path:
        print(f"Using file: {file_path}")
    else:
        file_path = "pcap_big.pcap"  # default
        print(f"No input given. Using default file: {file_path}")

    # Initialize traffic replay (for extracting domains) and async query manager (for reputation lookups)
    manager = TrafficReplayManager(file_path)
    query_manager = AsyncQueryManager(rps=5)  # 5 requests per second

    # Install Ctrl+C handler for graceful shutdown
    signal.signal(signal.SIGINT, lambda s, f: graceful_shutdown(manager, query_manager, s, f))
    print("Press Ctrl+C to stop the process gracefully.\n")

    # 1. Extract domains from the PCAP file
    start_time = time.time()
    print("Starting PCAP processing...")
    manager.extract_domains()

    # 2. Run asynchronous reputation queries for extracted domains
    print("Starting Reputation queries...")
    try:
        asyncio.run(query_manager.query_domains(manager.domains))
        results = asyncio.run(query_manager.query_domains(manager.domains))
    except asyncio.exceptions.CancelledError:
        # TODO: Add proper logging/prints for cancellation
        sys.exit(1)

    # 3. Compute and display final statistics, then save results to CSV
    total_time = time.time() - start_time
    final_statistics(manager, results, total_time)
    save_results_csv(results, csv_file="results.csv", source_file=file_path)

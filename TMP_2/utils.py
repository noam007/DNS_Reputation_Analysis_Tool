import json
import csv
import statistics


def graceful_shutdown(manager,  query_manager, signum, frame):
    print(f"\nCtrl+C detected (signal {signum})! Stopping gracefully...")
    manager.stop_event.set()
    query_manager.cancel_all_tasks()

def save_results_json(results, json_file="results.json"):
    """
    results: list of dicts (from the Reputation function)
    json_file: filename to save
    """
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4, ensure_ascii=False)
    print(f"Results saved to '{json_file}'")


def save_results_csv(results, csv_file="results.csv", source_file="pcap_single.pcap"):

    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Domain", "Reputation", "Classification", "Categories", "Source", "Response Time"])

        for r in results:
            domain = r.get("domain")
            reputation = r.get("reputation", 0)
            classification = "Trusted" if reputation >= 61 else "Untrusted"
            categories = ",".join(r.get("categories", [])) if isinstance(r.get("categories"), list) else r.get("categories", "{}")
            response_time = r.get("response_time", 0)

            writer.writerow([domain, reputation, classification, categories, source_file, f"{response_time:.3f}"])
    print(f"Results saved to CSV '{csv_file}'")


def final_statistics(manager, results, total_time):
    response_times = [r.get("response_time") for r in results if r.get("response_time") is not None]
    total_requests = len(results)
    total_domains = len(set(manager.domains))
    qps = total_requests / total_time if total_time > 0 else 0
    avg_time = statistics.mean(response_times) if response_times else 0
    min_time = min(response_times) if response_times else 0
    max_time = max(response_times) if response_times else 0

    print("\n--- Final Statistics ---")
    print(f"Packets processed: {manager.packets_sent}")
    print(f"Domains processed: {manager.domains_processed}")
    print(f"Errors encountered: {manager.errors}")
    print(f"Query rate (QPS): {qps:.2f}",'\n')

    print(f"Total requests: {total_requests}")
    print(f"Total unique domains: {total_domains}")
    print(f"Query rate (QPS): {qps:.2f}")
    print(f"Response time (avg/min/max): {avg_time:.3f}s / {min_time:.3f}s / {max_time:.3f}s")

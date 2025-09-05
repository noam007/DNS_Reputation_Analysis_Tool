import json

def graceful_shutdown(manager, signum, frame):
    print(f"\nCtrl+C detected (signal {signum})! Stopping gracefully...")
    manager.is_running = False

def final_statistics(manager,qps):
    print("\n--- Final Statistics ---")
    print(f"Packets processed: {manager.packets_sent}")
    print(f"Domains processed: {manager.domains_processed}")
    print(f"Errors encountered: {manager.errors}")
    print(f"Query rate (QPS): {qps:.2f}")


def save_results_json(results, json_file="results.json"):
    """
    results: רשימה של dict (מהפונקציה Reputation)
    json_file: שם הקובץ לשמירה
    """
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4, ensure_ascii=False)
    print(f"Results saved to '{json_file}'")
import asyncio
import logging
import json
from pathlib import Path
# from dns_reputation_tool import TrafficReplayManager

logging.basicConfig(level=logging.INFO)

async def example_basic_analysis():
    pcap_file = "sample_dns_traffic.pcap"
    if not Path(pcap_file).exists():
        print(f"PCAP file {pcap_file} not found.")
        return

    manager = TrafficReplayManager(
        pcap_file=pcap_file,
        output_dir="example_output",
        rate_limit=5.0,
        timeout=120
    )

    print("Starting DNS reputation analysis...")
    success = await manager.run_analysis()
    print("Analysis completed!" if success else "Analysis failed.")

def create_sample_config():
    config = {
        "api": {
            "base_url": "https://microcks.gin.dev.securingsam.io/rest/Reputation+API/1.0.0/domain/ranking",
            "headers": {"Authorization": "Token I_am_under_stress_when_I_test"},
            "timeout": 5.0,
            "max_retries": 3
        },
        "engine": {
            "rate_limit_rps": 10.0,
            "cache_ttl_seconds": 3600,
            "max_concurrent_requests": 50
        },
        "analysis": {
            "default_timeout": 300,
            "reputation_thresholds": {"trusted_min": 61, "untrusted_max": 60}
        }
    }
    with open("sample_config.json", "w") as f:
        json.dump(config, f, indent=2)
    print("Sample configuration saved to sample_config.json")

if __name__ == "__main__":
    print("DNS Reputation Analysis Tool - Examples")
    print("1. Creating sample configuration...")
    create_sample_config()
    print("\n2. To run basic analysis:")
    print("   python dns_reputation_tool.py your_pcap_file.pcap")
    asyncio.run(example_basic_analysis())

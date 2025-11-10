import json
import argparse
from datetime import datetime, timedelta
import os
import logging
from cvpysdk.commcell import Commcell
from cachetools import cached, TTLCache

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_config():
    """Loads the CommCell configuration from the config.json file."""
    try:
        with open('config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logging.error("Error: config.json file not found. Please create it.")
        return None
    except json.JSONDecodeError:
        logging.error("Error: Could not decode config.json. Please check the file format.")
        return None

def main():
    """Main function to run the script."""
    parser = argparse.ArgumentParser(description='Search for client details in CommCells.')
    parser.add_argument('region', choices=['HK', 'UK', 'US'], help='The region to search in.')
    parser.add_argument('client_name', help='The name of the client to search for.')
    args = parser.parse_args()

    config = load_config()
    if not config:
        return

    client_name = args.client_name
    region = args.region

    commcells_in_region = [c for c in config['commcells'] if c['region'] == region]

    if not commcells_in_region:
        logging.info(f"No CommCells found in the {region} region.")
        return

    results = {}
    commcell_caches = {commcell_info['name']: TTLCache(maxsize=1, ttl=7200) for commcell_info in commcells_in_region}

    for commcell_info in commcells_in_region:
        try:
            commcell = Commcell(commcell_info['name'], commcell_info['username'], commcell_info['password'])
            logging.info(f"Connected to CommCell: {commcell_info['name']}")

            @cached(commcell_caches[commcell_info['name']])
            def get_all_clients():
                """Fetches all clients from the Commcell."""
                logging.info(f"Fetching clients from {commcell_info['name']}...")
                return commcell.clients.all_clients

            clients = get_all_clients()

            for client_id, client_properties in clients.items():
                if client_name.lower() in client_properties['client_name'].lower():
                    client = commcell.clients.get(client_id)

                    client_key = (commcell_info['name'], client.client_id)
                    if client_key not in results:
                        results[client_key] = {
                            "CommCell": commcell_info['name'],
                            "Client Name": client.client_name,
                            "Client ID": client.client_id,
                            "Agents": [],
                            "Latest Backup": "N/A"
                        }

                    agents_found = []
                    if client.agents.has_agent('File System'):
                        agents_found.append('File System')

                    if client.agents.has_agent('Virtual Server'):
                        agents_found.append('Virtual Server')

                    if agents_found:
                        results[client_key]["Agents"].extend(agents_found)
                        try:
                            jobs = client.jobs.all_jobs
                            if jobs:
                                latest_backup_job = max(jobs.values(), key=lambda j: j.start_timestamp)
                                latest_backup_time = datetime.fromtimestamp(latest_backup_job.start_timestamp).strftime('%Y-%m-%d %H:%M:%S')
                                results[client_key]["Latest Backup"] = latest_backup_time
                        except Exception as e:
                            logging.warning(f"Could not retrieve latest backup for {client.client_name}: {e}")

            commcell.logout()

        except Exception as e:
            logging.error(f"Failed to connect or process CommCell {commcell_info['name']}: {e}")

    final_results = [result for result in results.values() if result["Agents"]]

    if final_results:
        print("\n--- Search Results ---")
        for result in final_results:
            print(f"  CommCell: {result['CommCell']}")
            print(f"  Client Name: {result['Client Name']}")
            print(f"  Client ID: {result['Client ID']}")
            print(f"  Agents: {', '.join(result['Agents'])}")
            print(f"  Latest Backup: {result['Latest Backup']}")
            print("  " + "-"*20)
    else:
        print("No clients found with the specified name and agents.")

if __name__ == "__main__":
    main()

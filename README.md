# CommCell Client Search

This script allows you to search for client details in CommCells based on a specified region and client name.

## Features

- **Region-Based Search:** Search for clients in specific regions (HK, UK, US).
- **Case-Insensitive Search:** The client name search is case-insensitive.
- **Agent Information:** Checks for the presence of the File System agent and Virtual Server agent.
- **Latest Backup Information:** Retrieves the latest backup time for each client.
- **Caching:** Caches the client list from each CommCell for 2 hours to reduce API calls.
- **Pagination:** Uses pagination when retrieving the client list to handle large datasets.

## Prerequisites

- Python 3.6 or higher
- `pip` for installing Python packages

## Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/get_client_details_commvault.git
   cd get_client_details_commvault
   ```

2. **Create a `config.json` file:**
   Create a `config.json` file in the root of the project and add the CommCell connection details in the following format:
   ```json
   {
     "commcells": [
       {
         "name": "commcell1_hostname",
         "username": "your_username",
         "password": "your_password",
         "region": "HK"
       },
       {
         "name": "commcell2_hostname",
         "username": "your_username",
         "password": "your_password",
         "region": "UK"
       },
       {
         "name": "commcell3_hostname",
         "username": "your_username",
         "password": "your_password",
         "region": "US"
       }
     ]
   }
   ```
   **Note:** Replace the placeholder values with your actual CommCell details.

3. **Install the required dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

To run the script, use the following command:

```bash
python commcell_client_search.py <region> <client_name>
```

### Arguments

- `region`: The region to search in. Choose from `HK`, `UK`, or `US`.
- `client_name`: The name of the client to search for (case-insensitive).

### Example

```bash
python commcell_client_search.py US my_client
```

This command will search for clients with "my_client" in their name in all CommCells located in the US region. The script will then display the client's details, including the CommCell it belongs to, its client ID, the agents present (File System or Virtual Server), and the latest backup time.

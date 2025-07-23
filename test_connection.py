

import requests
import os

# --- Configuration ---
# Ensure we use the correct settings you've confirmed work.
url = "https://127.0.0.1:27124/"
api_key = "8e6e22d4025259118d98ca11bf5f99b2f01ab2fd88f2abe6726decf4f033a330"
headers = {
    "Authorization": f"Bearer {api_key}",
    "accept": "application/json"
}

# --- Execution ---
print(f"Attempting to connect to: {url}")
print(f"Using API Key ending in: ...{api_key[-4:]}")

try:
    # verify=False is equivalent to curl's -k flag, to ignore self-signed SSL certificate errors.
    # timeout=10 gives it 10 seconds to respond.
    response = requests.get(url, headers=headers, verify=False, timeout=10)
    
    print(f"\n--- SUCCESS ---")
    print(f"Status Code: {response.status_code}")
    
    # Try to print JSON body, fall back to raw text if it's not JSON
    try:
        print("\nBody:")
        print(response.json())
    except requests.exceptions.JSONDecodeError:
        print("\nBody (not JSON):")
        print(response.text)

except requests.exceptions.RequestException as e:
    print(f"\n--- FAILURE ---")
    print(f"An error occurred: {e}")

finally:
    print("\n--- Test Complete ---")


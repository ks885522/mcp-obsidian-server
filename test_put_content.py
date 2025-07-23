

import requests
import urllib.parse

# --- Configuration ---
# Use the confirmed working settings
protocol = "https"
host = "127.0.0.1"
port = 27124
api_key = "8e6e22d4025259118d98ca11bf5f99b2f01ab2fd88f2abe6726decf4f033a330"

# --- PUT Request Details ---
file_to_write = "test_from_script.md"
content_to_write = "Hello from the Python test script! If you see this, the PUT request worked."

# URL encode the filepath to handle spaces or special characters
encoded_file_path = urllib.parse.quote(file_to_write)
url = f"{protocol}://{host}:{port}/vault/{encoded_file_path}"

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "text/markdown"
}

# --- Execution ---
print(f"Attempting to PUT content to: {url}")
print(f"Using API Key ending in: ...{api_key[-4:]}")

try:
    # verify=False is equivalent to curl's -k flag
    # Using a generous timeout to see if it hangs
    response = requests.put(
        url, 
        headers=headers, 
        data=content_to_write.encode('utf-8'), # Send content as UTF-8 bytes
        verify=False, 
        timeout=20
    )
    
    print(f"\n--- SUCCESS ---")
    print(f"Status Code: {response.status_code}")
    
    if response.status_code in [200, 204]:
        print("Request was successful. Check for 'test_from_script.md' in your vault.")
    else:
        print("Request returned a non-success status code.")

    print("\nResponse Body:")
    print(response.text)

except requests.exceptions.RequestException as e:
    print(f"\n--- FAILURE ---")
    print(f"An error occurred: {e}")

finally:
    print("\n--- Test Complete ---")


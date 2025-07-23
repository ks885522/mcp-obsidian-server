
import asyncio
import requests
import urllib.parse
import time

# --- Configuration ---
# Use the same confirmed working settings
protocol = "https"
host = "127.0.0.1"
port = 27124
api_key = "8e6e22d4025259118d98ca11bf5f99b2f01ab2fd88f2abe6726decf4f033a330"
file_to_write = "test_from_async_block.md"
content_to_write = f"Hello from the async blocking test at {time.time()}."

# --- The Synchronous Function ---
# This function simulates the blocking call inside obsidian.py
def synchronous_put_request():
    """
    This is a regular, synchronous function that uses the requests library.
    It will block the thread it runs on.
    """
    print("\n>>> [SYNC_TASK] Starting the blocking requests.put() call...", flush=True)
    
    encoded_file_path = urllib.parse.quote(file_to_write)
    url = f"{protocol}://{host}:{port}/vault/{encoded_file_path}"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "text/markdown"
    }
    
    try:
        response = requests.put(
            url, 
            headers=headers, 
            data=content_to_write.encode('utf-8'), 
            verify=False, 
            timeout=20
        )
        print(f">>> [SYNC_TASK] Blocking call finished with status: {response.status_code}", flush=True)
    except requests.exceptions.RequestException as e:
        print(f">>> [SYNC_TASK] Blocking call failed with error: {e}", flush=True)

# --- The Asynchronous "Canary" ---
# This task helps us see if the event loop is alive.
async def canary_task():
    """
    If this task stops printing, the event loop is blocked.
    """
    counter = 0
    while True:
        print(f"--- [CANARY] Event loop is alive! (Counter: {counter})", flush=True)
        counter += 1
        await asyncio.sleep(0.5)

# --- The Main Async Function ---
# This simulates the mcp-obsidian-server's event loop.
async def main():
    print("--- Experiment Start ---", flush=True)
    print("Starting the 'canary' task to monitor the event loop.", flush=True)
    
    canary = asyncio.create_task(canary_task())
    
    # Wait a moment to see the canary running
    await asyncio.sleep(1.5)
    
    print("\n--- Main Task ---", flush=True)
    print("About to call the SYNCHRONOUS put request directly from our async main function.", flush=True)
    print("Watch the 'CANARY' output. If it stops, we have proven the block.", flush=True)
    
    # This is the critical line: calling a blocking function directly in an async context
    synchronous_put_request()
    
    print("\n--- Main Task ---", flush=True)
    print("The synchronous function has completed and returned control.", flush=True)
    print("The 'CANARY' should now resume if it was blocked.", flush=True)
    
    # Let the canary run for a couple more seconds to show it has recovered
    await asyncio.sleep(2)
    
    canary.cancel()
    try:
        await canary
    except asyncio.CancelledError:
        print("\n--- Experiment End ---", flush=True)
        print("Canary task successfully cancelled.", flush=True)

if __name__ == "__main__":
    asyncio.run(main())

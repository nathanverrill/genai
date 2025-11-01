import requests
import threading
import os
import sys
import time
import uuid

# --- 1. Setup ---

# Address of your running LiteLLM proxy
LITELLM_PROXY_URL = "http://127.0.0.1:4000"

# --- Fetch model list from the proxy ---
print(f"Fetching model list from {LITELLM_PROXY_URL}/models ...")
try:
    response = requests.get(f"{LITELLM_PROXY_URL}/models")
    response.raise_for_status() # Raise an error if the request failed
    model_data = response.json()
    model_names = [model['id'] for model in model_data.get('data', [])]
    
    if not model_names:
        print("Error: No models found at the proxy endpoint.")
        sys.exit(1)

    print(f"Found {len(model_names)} models to test via proxy.")

except requests.exceptions.ConnectionError:
    print(f"Error: Could not connect to LiteLLM proxy at {LITELLM_PROXY_URL}.")
    print("Please ensure the proxy is running and accessible.")
    sys.exit(1)
except Exception as e:
    print(f"Error fetching model list: {e}")
    sys.exit(1)


# --- 2. Define the Task ---

# Define the prompt we will send to all models
PROMPT = "Explain the concept of 'separation of concerns' in software engineering in a single, simple sentence."
messages = [{"role": "user", "content": PROMPT}]

# We'll use a unique trace_id just to group our print statements
comparison_trace_id = f"model-comparison-{uuid.uuid4()}"
print(f"Using Trace ID for this run: {comparison_trace_id}")

# This function will be called by each thread
def call_model(model_name):
    """
    Calls a single model using the 'requests' library.
    This bypasses all litellm/openai client logic.
    """
    print(f"--- Calling: {model_name} ---")
    try:
        # This is the standard OpenAI-compatible chat completions endpoint
        endpoint = f"{LITELLM_PROXY_URL}/chat/completions"
        
        headers = {
            "Content-Type": "application/json"
        }
        
        body = {
            "model": model_name,
            "messages": messages
        }
        
        response = requests.post(endpoint, headers=headers, json=body, timeout=30)
        
        # Raise an error if the API call itself failed
        response.raise_for_status() 
        
        response_json = response.json()
        
        # Extract the response text
        response_text = response_json['choices'][0]['message']['content'].strip()
        print(f"✅ Response from {model_name}:\n{response_text}\n")
        
    except Exception as e:
        # Handle any errors (e.g., timeouts, API errors)
        print(f"❌ ERROR from {model_name}: {e}\n")

# --- 3. Run the Comparison ---

if __name__ == "__main__":
    threads = []
    
    # Create and start a thread for each model
    for model in model_names:
        thread = threading.Thread(target=call_model, args=(model,))
        threads.append(thread)
        thread.start()
        # Small delay to avoid hitting rate limits all at once
        time.sleep(0.1) 

    # Wait for all threads (models) to complete
    print(f"Waiting for all {len(threads)} models to respond...")
    for thread in threads:
        thread.join()

    print("--- All model calls complete. ---")
    print(f"Run {comparison_trace_id} finished. (No traces were sent to Phoenix).")

import requests

# Define the local endpoint
API_URL = "http://172.23.128.1:11434/api/generate"

def query_orca_mini(prompt):
    """
    Sends a prompt to the local Orca-Mini API and returns the response.
    """
    headers = {
        "Content-Type": "application/json",
    }
    data = {
        "model": "orca-mini",  # Specify the model name
        "prompt": prompt,      # The user's prompt
        "stream": False        # Optional: Disable streaming if not needed
    }

    try:
        # Send POST request
        response = requests.post(API_URL, json=data, headers=headers)
        response.raise_for_status()  # Raise an error for bad HTTP responses
        return response.json().get("response", "No output returned")  # Extract the response field
    except requests.exceptions.RequestException as e:
        return f"Error querying Orca-Mini API: {e}"

if __name__ == "__main__":
    prompt = "Why is the sky blue?"
    print(f"Query: {prompt}")
    response = query_orca_mini(prompt)
    print(f"Response: {response}")

import requests
import base64
import os
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

# Define the API endpoint URL
url  = os.getenv("DEV_URL") 
print(url)

# Set up the credentials for basic authentication
username = os.getenv("DEV_PNG_USERNAME")
password = os.getenv("DEV_PNG_PASSWORD")

# Create the Basic Auth header
credentials = f"{username}:{password}"
b64_credentials = base64.b64encode(credentials.encode()).decode()

headers = {
    "Authorization": f"Basic {b64_credentials}",
    "Accept": "text/csv" 
}


def get_logs():
    # Make the GET request with headers
    response = requests.get(url, headers=headers)

    # Check the response status
    if response.status_code == 200:
        # If successful, write the content to a CSV file
        with open("logs.csv", "wb") as f:
            f.write(response.content)
        print("CSV file downloaded successfully.")
    elif response.status_code == 401:
        print("Authentication failed: Invalid credentials.")
    else:
        print(f"Failed to retrieve the CSV file. Status code: {response.status_code}")

if __name__ == "__main__":
    get_logs()
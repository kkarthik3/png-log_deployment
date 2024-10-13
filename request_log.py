import requests
import base64
import os
from dotenv import load_dotenv

load_dotenv()

# Define the API endpoint URLs
urls = {
    "dev": os.getenv("DEV_URL"),
    "prod": os.getenv("PROD_URL")
}

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

def get_logs(stage: str):
    stage = stage.lower()
    url = urls.get(stage)
    
    if not url:
        print(f"Invalid stage: {stage}. Please specify 'dev' or 'prod'.")
        return
    
    # Make the GET request
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        # Write the content to a CSV file
        file_name = f"{stage}.csv"
        with open(file_name, "wb") as f:
            f.write(response.content)
        print(f"CSV file downloaded successfully: {file_name}")
    elif response.status_code == 401:
        print("Authentication failed: Invalid credentials.")
    else:
        print(f"Failed to retrieve the CSV file. Status code: {response.status_code}")

if __name__ == "__main__":
    get_logs("prod")

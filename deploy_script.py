import os
import json
import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

AI_BUILDER_TOKEN = os.getenv("AI_BUILDER_TOKEN")
if not AI_BUILDER_TOKEN:
    print("Error: AI_BUILDER_TOKEN not found in environment")
    exit(1)

# Read config
try:
    with open("deploy-config.json", "r") as f:
        config = json.load(f)
except FileNotFoundError:
    print("Error: deploy-config.json not found")
    exit(1)

# API Endpoint
API_URL = "https://space.ai-builders.com/backend/v1/deployments"

headers = {
    "Authorization": f"Bearer {AI_BUILDER_TOKEN}",
    "Content-Type": "application/json"
}

payload = {
    "repo_url": config["repo_url"],
    "service_name": config["service_name"],
    "branch": config["branch"],
    "port": config["port"],
    "env_vars": config.get("env_vars", {})
}

print(f"Deploying {config['service_name']} from {config['repo_url']}...")
print(f"Target: {API_URL}")

try:
    response = httpx.post(API_URL, headers=headers, json=payload, timeout=60.0)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code in [200, 201]:
        print("Deployment triggered successfully!")
        print(json.dumps(response.json(), indent=2))
    else:
        print("Deployment failed.")
        print(response.text)
except Exception as e:
    print(f"An error occurred: {str(e)}")

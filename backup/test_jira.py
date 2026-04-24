import os
from dotenv import load_dotenv

import requests  #Python library for makin any HTTP requests, used to interact with the Jira API.
from requests.auth import HTTPBasicAuth  #to ahndle basic auth when making requests to the Jira API. It allows you to provide your Jira email and API token for authentication.

print("Step 1: script started")

load_dotenv()
print("Step 2: .env loaded")

jira_base_url = os.getenv("JIRA_BASE_URL")
jira_email = os.getenv("JIRA_EMAIL")
jira_api_token = os.getenv("JIRA_API_TOKEN")
jira_project_key = os.getenv("JIRA_PROJECT_KEY")

print("Step 3: jira_base_url =", jira_base_url)
print("Step 4: jira_email found =", bool(jira_email))
print("Step 5: jira_api_token found =", bool(jira_api_token))
print("Step 6: jira_project_key =", jira_project_key)

if not jira_base_url or not jira_email or not jira_api_token or not jira_project_key:
    raise ValueError("Missing Jira values in .env file")

url = f"{jira_base_url}/rest/api/3/issue"
print("Step 7: URL =", url)

payload = {
    "fields": {
        "project": {
            "key": jira_project_key
        },
        "summary": "Test Jira issue from Python",
        "description": {
            "type": "doc",
            "version": 1,
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        {
                            "type": "text",
                            "text": "This issue was created from Python API call."
                        }
                    ]
                }
            ]
        },
        "issuetype": {
            "name": "Task"
        }
    }
}

print("Step 8: payload built")

response = requests.post(
    url,
    json=payload,
    auth=HTTPBasicAuth(jira_email, jira_api_token),
    headers={
        "Accept": "application/json",
        "Content-Type": "application/json"
    },
    timeout=30
)

print("Step 9: request sent")
print("Status:", response.status_code)
print("Response:", response.text)
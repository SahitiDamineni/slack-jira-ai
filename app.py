import threading
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
from dotenv import load_dotenv
from groq_helper import call_groq, call_groq_simple, classify_user_intent

# slack imports
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

# Requests imports for Jira API interaction
import requests  # Python library for makin any HTTP requests, used to interact with the Jira API.
from requests.auth import (HTTPBasicAuth)  # to ahndle basic auth when making requests to the Jira API. It allows you to provide your Jira email and API token for authentication.

# load environment variables from .env file
load_dotenv()



# Slack values
slack_bot_token = os.getenv("SLACK_BOT_TOKEN")
slack_app_token = os.getenv("SLACK_APP_TOKEN")

# Jira values
jira_base_url = os.getenv("JIRA_BASE_URL")
jira_email = os.getenv("JIRA_EMAIL")
jira_api_token = os.getenv("JIRA_API_TOKEN")
jira_project_key = os.getenv("JIRA_PROJECT_KEY")

# Groq values
groq_api_key = os.getenv("GROQ_API_KEY")
groq_model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")


# verify that all required environment variables are present
if not slack_bot_token or not slack_app_token:
    raise ValueError("Missing SLACK_BOT_TOKEN or SLACK_APP_TOKEN in .env file")

if not jira_base_url or not jira_email or not jira_api_token or not jira_project_key:
    raise ValueError("Missing Jira values in .env file")

if not groq_api_key:
    raise ValueError("Missing GROQ_API_KEY in .env file")

# initialize the Slack app with the bot token
app = App(token=slack_bot_token)

def is_help_request(text: str) -> bool:
    help_keywords = ["help", "what can you do", "how to create jira", "commands"]
    return any(keyword in text.lower() for keyword in help_keywords)

@app.event("message")
def handle_message(event, say):
    if event.get("bot_id"):
        return

    text = event.get("text", "").strip()

    if not text:
        return

    try:
        if is_help_request(text):
            say(
                "I can chat with you or create Jira issues.\n\n"
                "To create Jira, say:\n"
                "- create jira for payment failure\n"
                "- create bug for login error\n"
                "- create story for retry logic\n\n"
                "You can also use: `/story <details>`"
            )
            return

        intent_result = classify_user_intent(text)

        if intent_result["intent"] == "create_jira":
            say(
                text="⚙️ It looks like you want a Jira issue. Creating it now...",thread_ts=event["ts"]
            )

            story_details = call_groq(text)
            jira = create_jira_issue(story_details)

            key = jira["key"]
            url = f"{jira_base_url}/browse/{key}"

            say(
                text=(
                    f"Created Jira issue: {key} "
                    f"[{story_details['issue_type']}, {story_details['priority']}] - "
                    f"{story_details['title']}\n"
                    f"{url}"
                ),
               thread_ts=event["ts"]
            )
        else:
            reply = call_groq_simple(text)
            say(reply)

    except Exception as e:
        say(f"❌ Error: {str(e)}") 
        
@app.event("app_mention")
def handle_mention(event, say):
    if event.get("bot_id"):
        return

    text = event.get("text", "").strip()

    if not text:
        return

    try:
        # Only create Jira when user clearly asks for it
        jira_keywords = ["create jira", "create ticket", "create issue", "create bug", "create story"]

        if any(keyword in text.lower() for keyword in jira_keywords):
            say("⚙️ Creating Jira issue from your message...")

            story_details = call_groq(text)
            jira = create_jira_issue(story_details)

            key = jira["key"]
            url = f"{jira_base_url}/browse/{key}"

            say(
                f"Created Jira issue: {key} "
                f"[{story_details['issue_type']}, {story_details['priority']}] - "
                f"{story_details['title']}\n"
                f"{url}"
            )
        else:
            reply = call_groq_simple(text)
            say(reply)

    except Exception as e:
        say(f"❌ Error: {str(e)}")
    
    
# When user type /story this funtion will be triggered. It extracts the text after command and uses it to create a Jira issue. It also handles responses back to the user in Slack, confirming whether the issue was created successfully or if there was an error.
@app.command("/story")
def handle_story(ack, respond, command):
    ack()

    minutes = command.get("text", "").strip()

    if not minutes:
        respond("Please provide meeting notes.")
        return

    try:
        respond("⚙️ Processing with local AI...")

        storyDetailsfromAI = call_groq(minutes)
        print("DEBUG - LLM OUTPUT:", storyDetailsfromAI)

        jira = create_jira_issue(storyDetailsfromAI)
        print("DEBUG - JIRA RESPONSE:", jira)

        key = jira["key"]
        url = f"{jira_base_url}/browse/{key}"

        respond(
            f"Created Jira issue: {key} "
            f"[{storyDetailsfromAI['issue_type']}, {storyDetailsfromAI['priority']}] - "
            f"{storyDetailsfromAI['title']}\n"
            f"{url}"
        )

    except Exception as e:
        respond(f"❌ Error: {str(e)}")


# This function takes the structured story details generated by the AI and creates a Jira issue using the Jira REST API. It constructs the appropriate payload for the API request, including the project key, summary, description (formatted as a rich text document), and issue type. It then makes a POST request to the Jira API endpoint to create the issue and returns the response.
def create_jira_issue(story):
    url = f"{jira_base_url}/rest/api/3/issue"
    print("DEBUG - JIRA url:", url)

    payload = {
        "fields": {
            "project": {"key": jira_project_key},
            "summary": f"[{story['issue_type']}, {story['priority']}] - {story['title']}",
            "description": jira_description_doc(
                story["description"], story["acceptance_criteria"]
            ),
            "issuetype": {"name": "Task"},
        }
    }
    print("DEBUG - JIRA payload:", payload)

    response = requests.post(
        url,
        json=payload,
        auth=HTTPBasicAuth(jira_email, jira_api_token),
        headers={"Accept": "application/json", "Content-Type": "application/json"},
    )

    response.raise_for_status()
    return response.json()

# This function formats the description and acceptance criteria into a rich text document format that Jira can render properly. It takes the description and acceptance criteria as input and constructs a structured document with paragraphs and bullet points for the acceptance criteria.
def jira_description_doc(description, acceptance):
    ac_text = "\n".join([f"- {a}" for a in acceptance])

    return {
        "type": "doc",
        "version": 1,
        "content": [
            {
                "type": "paragraph",
                "content": [
                    {
                        "type": "text",
                        "text": f"{description}\n\nAcceptance Criteria:\n{ac_text}",
                    }
                ],
            }
        ],
    }
  
@app.event("app_home_opened")
def update_home_tab(client, event):
    client.views_publish(
        user_id=event["user"],
        view={
            "type": "home",
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "Jira Story Create"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": (
                            "*What I can do:*\n"
                            "• Chat with you normally\n"
                            "• Create Jira issues from your messages\n\n"
                            "*Examples:*\n"
                            "• `create jira for payment failure`\n"
                            "• `create bug for login error`\n"
                            "• `create story for retry logic`\n"
                            "• `/story upgrade Java 17 to 21`"
                        )
                    }
                }
            ]
        }
    )  

# Start the Slack app using Socket Mode, which allows it to receive events and commands from Slack. The handler listens for incoming connections and starts the app.
if __name__ == "__main__":
    handler = SocketModeHandler(app, slack_app_token)
    handler.start()

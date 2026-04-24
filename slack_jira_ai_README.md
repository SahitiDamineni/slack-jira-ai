# Slack → Local LLM → Jira Workflow

This README documents the full setup and runbook for a local AI workflow:

```text
Slack slash command
   ↓
Python Slack Bolt app
   ↓
Local LLM using Ollama
   ↓
Jira REST API
   ↓
Slack response with Jira issue link
```

The goal of this project is to practice AI workflow orchestration, Slack app setup, Jira API integration, local LLM usage, and debugging.

---

## 1. Final Workflow Overview

```text
[Slack UI]
   │
   │  (1) User types slash command: /story <meeting notes>
   ▼
[Slack Server]
   │
   │  (2) Sends event through Socket Mode over WebSocket
   ▼
[Python App using Slack Bolt]
   │
   │  (3) Reads command text
   ▼
[Local LLM using Ollama]
   │
   │  (4) Converts meeting notes into Jira fields
   ▼
[Python App]
   │
   │  (5) Builds Jira JSON payload
   │  (6) Calls Jira REST API
   ▼
[Jira Cloud]
   │
   │  (7) Creates Jira task
   ▼
[Python App]
   │
   │  (8) Sends Jira issue link back to Slack
   ▼
[Slack UI]
```

---

## 2. Frameworks and Tools Used

| Tool / Framework | Purpose |
|---|---|
| Slack App | Cloud-side identity and configuration for the Slack integration |
| Slack Bolt for Python | Python framework to handle Slack slash commands and events |
| Socket Mode | Lets local Python app receive Slack events over WebSocket without public URL |
| Python | Backend runtime for workflow logic |
| python-dotenv | Loads secrets from `.env` file |
| requests | Sends HTTP API requests to Jira and Ollama |
| Jira REST API | Creates Jira issues from Python |
| Ollama | Runs local LLM on laptop |
| qwen2.5:0.5b | Lightweight local LLM used for testing |
| VS Code | Code editor |
| Terminal | Run Python app, install packages, kill processes |

---

## 3. Key Concepts

### Slack App vs Python App vs Slack Bolt

| Concept | Meaning |
|---|---|
| Slack App | App identity/config created in Slack Developer Portal |
| Python App | Local code running on your laptop |
| Slack Bolt | Python framework used to connect Python app to Slack |

```text
Slack App = identity/config in Slack
Slack Bolt = Python framework
Python App = local runtime logic
```

### Tokens

| Token / Credential | Prefix | Used For | Runtime Used? |
|---|---|---|---|
| App-Level Token | `xapp-` | Socket Mode WebSocket connection | Yes |
| Bot Token | `xoxb-` | Sending/responding in Slack | Yes |
| Client ID | usually numeric/string | OAuth setup/install flow | Not used in this local runtime |
| Client Secret | secret string | OAuth token exchange | Not used in this local runtime |
| Signing Secret | string | Verify incoming HTTP requests | Not used with Socket Mode |

```text
xapp token = connect/listen
xoxb token = act/respond
```

Example:

```python
app = App(token=slack_bot_token)                  # bot token, used for Slack actions
handler = SocketModeHandler(app, slack_app_token) # app token, used for WebSocket connection
```

---

# Slack → Local LLM → Jira Workflow

---

## 1. Flow Overview

Slack (/story command) → Python (Slack Bolt + Socket Mode) → Local LLM (Ollama) → Jira API → Slack response

---

## 2. Tech Stack

- Slack App (UI + config)
- Slack Bolt (Python)
- Socket Mode (WebSocket)
- Python
- requests
- python-dotenv
- Jira REST API
- Ollama (local LLM)

---
# Slack → AI → Jira Automation (Step-by-Step Setup Guide)

## 1. Jira Setup

1. Get Base URL:
   - Open Jira in browser → Copy URL (e.g., https://your-domain.atlassian.net) → Add to `.env`: JIRA_BASE_URL=...

2. Get Project Key:
   - Open your Jira project → Top-left shows key (e.g., KAN) → Add to `.env`: JIRA_PROJECT_KEY=KAN

3. Create API Token:
   - Go to https://id.atlassian.com/manage-profile/security/api-tokens → Click Create API Token → Enter name → Click Create → Copy token → Add to `.env`: JIRA_API_TOKEN=... → Add email: JIRA_EMAIL=your-email

---

## 2. Slack Setup

1. Create Slack App:
   - Go to https://api.slack.com/apps → Click Create New App → Select From scratch → Enter App Name + Workspace → Click Create App

2. Basic Information:
   - Go to Basic Information → (Optional) Copy Client ID, Client Secret, Signing Secret (not used in this project)

3. Enable Socket Mode:
   - Go to Socket Mode → Turn ON Enable Socket Mode → Click Generate Token and Scopes → Enter Token Name: socket-token → Add scope: connections:write → Click Generate → Copy App-Level Token (xapp-xxxx) → Add to `.env`: SLACK_APP_TOKEN=xapp-xxxx

4. Add Bot Permissions:
   - Go to OAuth & Permissions → Under Bot Token Scopes → Click Add Scope → Add: commands → Add: chat:write

5. Install App:
   - Go to OAuth & Permissions → Click Install to Workspace → Approve → Copy Bot User OAuth Token (xoxb-xxxx) → Add to `.env`: SLACK_BOT_TOKEN=xoxb-xxxx

6. Create Slash Command:
   - Go to Slash Commands → Click Create New Command → Enter Command: /story → Description: Create Jira task → Usage Hint: meeting notes → Enter Request URL: https://example.com → Click Save

7. Reinstall App:
   - Go to OAuth & Permissions → Click Reinstall App → Approve

8. Add App to Channel -> Enables sending messages in channel by using /story command:
   - Open Slack channel → Type: /invite @YourAppName

9. Test:
   - Type: /story test message → Expect response from app

10. Enable Sending messages to the app/bot directly on Slack using /story command
   - This allows : DM with bot using /story command
   - Open Slack app -> https://api.slack.com/apps -> Click on the app -> App Home -> Enable Home Tab , Enable Messages Tab
   - Go to OAuth & Permissions -> Reinstall App

11. Enable sending message to app/ Bot and enable bot to react even without slack command - 
   - This allows: DM with bot with /story and general messages , @mention in channel where app is invited to
   - https://api.slack.com/apps → Your App → Event Subscriptions -> Turn ON: Enable Events -> Add Bot Events: app_mention , message.im, app_home_opened
   - Add Required Permissions -> OAuth & Permissions ->chat:write commands app_mentions:read im:read im:history
   - Reinstall App
   - Write event handling code in python

12. Enable app / bot to create stories without slash command
   - change python code


The app has to be running for it to work
---

## 3. Python Setup

1. Install Python
   -  Run: brew install python → Verify: python3 --version

2. Create Project
   - mkdir ~/Desktop/slack-jira-ai → cd ~/Desktop/slack-jira-ai

3. Create Virtual Environment:
   - python3 -m venv .venv → source .venv/bin/activate

2. Install Dependencies:
   - python -m pip install slack-bolt python-dotenv requests black flake8
   - pip install slack-bolt python-dotenv requests

3. Create `.env` file:
   - Add:
     SLACK_BOT_TOKEN=...
     SLACK_APP_TOKEN=...
     JIRA_BASE_URL=...
     JIRA_EMAIL=...
     JIRA_API_TOKEN=...
     JIRA_PROJECT_KEY=...
     GROQ_API_KEY=...
     GROQ_MODEL=llama-3.3-70b-versatile

---

## 4. Run Application

1. Start app:
   - python app.py

2. Test in Slack:
   - /story Add retry logic for failed payments

---

## 5. Flow

Slack → Groq API → Jira API → Issue Created → Slack response

---

## 6. Jira API

Endpoint:
POST /rest/api/3/issue

---

## 7. Commands

Run: python app.py  
Stop: Ctrl + C  
Kill: pkill -f python   ; pkill -9 -f python ; pkill -f app.py
Open preview mode : Cmd + Shift + V

---

## 8. VS Code Shortcuts

Theme: Cmd + K → Cmd + T  
Format: Shift + Option + F  
Command Palette: Cmd + Shift + P  
Indent: Tab / Shift + Tab  



## 9. AutoGenrate requirement.txt

source .venv/bin/activate 
pip freeze > requirements.txt

or
 
pip install pipreqs
pipreqs .

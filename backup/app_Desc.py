

# Phase 1: Setup - Load libraries
# Python application built using Slack Bolt SDK
import os                                                            #Build in python library which is used to interact with OS and Used to read values stored in .env file using os.getenv()
from dotenv import load_dotenv                                        #python-dotenv is a library that allows you to read key-value pairs from a .env file. load_dotenv loads the values from the .env file into the environment variables, making them accessible via os.getenv() or os.environ in your Python code.
from slack_bolt import App                                            #slack bolt is a framework for building Slack connected apps in Python. App is the main class that represents your Slack app . This helps connect to slack , handle event and API  interactions with Slack.
from slack_bolt.adapter.socket_mode import SocketModeHandler           #establishes and manages the WebSocket connection between your local app and Slack, so Slack can push events to your app without requiring a public HTTP endpoint.

print("Step 1: starting app.py")

# Phase 2: Setup - Load Tokens into environemtn varibales
load_dotenv()   #  This loads the variables from .env into the current runtime environment so they become available via os.getenv().
print("Step 2: .env loaded")

slack_bot_token = os.getenv("SLACK_BOT_TOKEN")    #token is used by slack app to perform actions in Slack, like replying, posting messages, or calling Slack APIs.
slack_app_token = os.getenv("SLACK_APP_TOKEN")    # token is used to establish a WebSocket connection between your app and Slack, allowing your app to receive real-time events and messages from Slack. 


print("Step 3: bot token found =", bool(slack_bot_token))
print("Step 4: app token found =", bool(slack_app_token))

if not slack_bot_token or not slack_app_token:       # if either token is missing, raise error to alert the developer that they need to provide these tokens in the .env file for the app to function properly.
    raise ValueError("Missing SLACK_BOT_TOKEN or SLACK_APP_TOKEN in .env file")

# Phase 3: Create Bolt app

# app = App(token=slack_bot_token)   #Creates your python bolt app instance using the bot token. allows app to authenticate with Slack and perform actions on behalf of the bot user.
# print("Step 5: Bolt app created")

# Phase 5: handle command

# @app.command("/story")    #when user types /story in slack, the function will be triggered.
# def handle_story(ack, respond, command):
#     print("Step 6: /story command received")
#     ack()            # ack the command was receieved. This is important to let Slack know that your app has received the command and is processing it. If you don't acknowledge, Slack will think your app is unresponsive and may show an error to the user.
#     text = command.get("text", "") # retrived the text after  the slash command
#     print("Step 7: command text =", text)
#     respond(f"✅ I received your text: {text}") #responds back to slack with message 


# # Phase 4: Open a websocker connection and start listening
# if __name__ == "__main__":             #only runs the following code if this script is executed directly 
#     print("Step 8: creating SocketModeHandler")
#     handler = SocketModeHandler(app, slack_app_token)  #creates an instance of Socketmodehandles and passes the python bolt app and app token. This sets up the connection between your app and Slack so that your app can receive events and messages in real time.
#     print("Step 9: starting Socket Mode")
#     # handler.start()      #starts socket mode, and app starts listening for events form slack. When a user types /story, the handle_story function will be triggered, and the app will respond with the received text.
#     print("Step 10: this line should normally not print immediately")

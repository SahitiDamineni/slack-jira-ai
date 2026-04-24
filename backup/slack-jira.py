
# import os                                                           
# from dotenv import load_dotenv 
# #slack imports                                      
# from slack_bolt import App                                            
# from slack_bolt.adapter.socket_mode import SocketModeHandler 
# #Requests imports for Jira API interaction 
# import requests  #Python library for makin any HTTP requests, used to interact with the Jira API.
# from requests.auth import HTTPBasicAuth  #to ahndle basic auth when making requests to the Jira API. It allows you to provide your Jira email and API token for authentication.


# #load environment variables from .env file
# load_dotenv()   


# # Slack values
# slack_bot_token = os.getenv("SLACK_BOT_TOKEN")    
# slack_app_token = os.getenv("SLACK_APP_TOKEN")   

# # Jira values
# jira_base_url = os.getenv("JIRA_BASE_URL")
# jira_email = os.getenv("JIRA_EMAIL")
# jira_api_token = os.getenv("JIRA_API_TOKEN")
# jira_project_key = os.getenv("JIRA_PROJECT_KEY")




# #verify that all required environment variables are present
# if not slack_bot_token or not slack_app_token:       
#     raise ValueError("Missing SLACK_BOT_TOKEN or SLACK_APP_TOKEN in .env file")


# if not jira_base_url or not jira_email or not jira_api_token or not jira_project_key:
#     raise ValueError("Missing Jira values in .env file")


# #initialize the Slack app with the bot token
# app = App(token=slack_bot_token)   


# #When user type /story this funtion will be triggered. It extracts the text after command and uses it to create a Jira issue. It also handles responses back to the user in Slack, confirming whether the issue was created successfully or if there was an error.
# @app.command("/story")
# def handle_story(ack, respond, command):
#     ack()

#     text = command.get("text", "").strip()
#     print("Step 4: /story command received")


#     if not text:
#         respond("Please provide some text. Example: `/story Create login retry task`")
#         return
 
#     # Calls the function to create a Jira issue and handles the response
#     # sending a confirmation message back to Slack with the issue key and URL if successful, or an error message if it fails.
#     try:
#         jira_response = create_jira_issue(text)
#         print("Step 5: jira_response =", jira_response)
#         issue_key = jira_response.get("key")
#         issue_url = f"{jira_base_url}/browse/{issue_key}"

#         respond(f"✅ Jira issue created: {issue_key}\n{issue_url}")

#     except Exception as e:
#         respond(f"❌ Failed to create Jira issue: {str(e)}")
 


# #This function is responsible for creating a Jira issue using the Jira REST API. It constructs the payload with the necessary fields, including the project key, summary, description, and issue type. It then makes a POST request to the Jira API endpoint for creating issues, using basic authentication with the provided Jira email and API token. If the request is successful, it returns the JSON response from Jira, which includes details about the created issue. If there is an error during the request, it raises an exception that can be caught and handled by the calling function.
# def create_jira_issue(summary_text: str) -> dict:
#     url = f"{jira_base_url}/rest/api/3/issue"

#     payload = {
#         "fields": {
#             "project": {
#                 "key": jira_project_key
#             },
#             "summary": summary_text,
#             "description": {
#                 "type": "doc",
#                 "version": 1,
#                 "content": [
#                     {
#                         "type": "paragraph",
#                         "content": [
#                             {
#                                 "type": "text",
#                                 "text": f"This Jira task was created from Slack using this input: {summary_text}"
#                             }
#                         ]
#                     }
#                 ]
#             },
#             "issuetype": {
#                 "name": "Task"
#             }
#         }
#     }

#     response = requests.post(
#         url,
#         json=payload,
#         auth=HTTPBasicAuth(jira_email, jira_api_token),
#         headers={
#             "Accept": "application/json",
#             "Content-Type": "application/json"
#         },
#         timeout=30
#     )

#     response.raise_for_status()
#     return response.json() 



# if __name__ == "__main__":             
#     handler = SocketModeHandler(app, slack_app_token) 
#     handler.start()  
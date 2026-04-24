
import os                                                           
from dotenv import load_dotenv                                        
from slack_bolt import App                                            
from slack_bolt.adapter.socket_mode import SocketModeHandler           

load_dotenv()   

slack_bot_token = os.getenv("SLACK_BOT_TOKEN")    
slack_app_token = os.getenv("SLACK_APP_TOKEN")   


if not slack_bot_token or not slack_app_token:       
    raise ValueError("Missing SLACK_BOT_TOKEN or SLACK_APP_TOKEN in .env file")

# app = App(token=slack_bot_token)   

# @app.command("/story")   
# def handle_story(ack, respond, command):
#     ack()   
#     text = command.get("text", "")       
#     respond(f"✅ I received your text: {text}") 

# if __name__ == "__main__":             
#     handler = SocketModeHandler(app, slack_app_token) 
    # handler.start()    

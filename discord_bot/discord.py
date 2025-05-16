#Connects to Discord's WebSocket gateway
#Listens for new messages in your specified channel
#Prints out messages from other users
#Automatically replies to those messages, mentioning the user and repeating their message content


import requests
import json
import websocket
import threading
import time
import random
import re
from dotenv import load_dotenv
import os
import agent

load_dotenv()

# Your personal token (keep this secret!)
USER_TOKEN = os.getenv("USER_TOKEN")

# The ID of the channel you want to monitor
CHANNEL_ID = os.getenv("CHANNEL_ID")

# Track last message time and last bot message time
last_message_time = time.time()

def send_message(channel_id, message_content, reply_to_message_id=None):
    global last_message_time
    

    headers = {
        "Authorization": USER_TOKEN,
        "Content-Type": "application/json"
    }
    
    payload = {
        "content": message_content
    }
    
    # If we're replying to a message, add the message reference
    if reply_to_message_id:
        payload["message_reference"] = {
            "message_id": reply_to_message_id,
            "channel_id": channel_id
        }
    
    api_url = f"https://discord.com/api/v9/channels/{channel_id}/messages"
    
    response = requests.post(api_url, headers=headers, json=payload)
    
    if response.status_code == 200:
        print("Message sent successfully!")
        last_message_time = time.time()  # Update last bot message time
    else:
        print(f"Failed to send message. Status code: {response.status_code}")
        print(f"Response: {response.text}")

def check_inactive():
    global last_message_time
    while True:
        current_time = time.time()
        time_since_last_message = current_time - last_message_time
        
        # Only send a new message if it's been at least X minutes since our last bot message
        if time_since_last_message >= 200:  
            print("Channel inactive for 5 minutes, sending conversation starter...")
            prompt = "Generate a random new conversation starter message"
            message = agent.call_agent(prompt)
            send_message(CHANNEL_ID, message)
        time.sleep(60)  # Check every minute

def on_message(ws, message):
    data = json.loads(message)
    
    # We only care about message creation events (op code 0, type "MESSAGE_CREATE")
    if data.get("op") == 0 and data.get("t") == "MESSAGE_CREATE":
        message_data = data.get("d", {})
        
        # Skip our own messages
        if message_data.get("author", {}).get("id") == get_user_id():
            return
            
        # Check if the message is in the channel we're monitoring
        if message_data.get("channel_id") == CHANNEL_ID:
            author = message_data.get("author", {}).get("username", "Unknown")
            content = message_data.get("content", "")
            message_id = message_data.get("id")
            
            # Check if bot is mentioned
            mentions = message_data.get("mentions", [])
            bot_mentioned = any(mention.get("id") == get_user_id() for mention in mentions)
            
            # Check if message is a direct reply to bot's message only
            referenced_message = message_data.get("referenced_message", {})
            replying_to_bot = False
            if referenced_message:
                # Only set to True if the referenced message is from our bot
                if referenced_message.get("author", {}).get("id") == get_user_id():
                    replying_to_bot = True
            
            print(f"Message from {author}: {content}")
            
            # Only respond if bot is mentioned or message is directly replying to bot
            if bot_mentioned or replying_to_bot:
                # Generate response using agent
                response = agent.call_agent(content)
                
                # Add delay before responding
                time.sleep(120)  # Reduced delay to 2 seconds for better interaction
                
                # Send response as reply
                send_message(CHANNEL_ID, response, message_id)

def on_error(ws, error):
    print(f"Error: {error}")

def on_close(ws, close_status_code, close_msg):
    print("Connection closed")

def on_open(ws):
    print("Connection established")
    
    # Send identify payload
    identify_payload = {
        "op": 2,
        "d": {
            "token": USER_TOKEN,
            "properties": {
                "$os": "windows",
                "$browser": "chrome",
                "$device": "pc"
            },
            "presence": {
                "status": "online",
                "afk": False
            }
        }
    }
    
    ws.send(json.dumps(identify_payload))
    
    # Start heartbeat thread
    def heartbeat(interval):
        while True:
            heartbeat_payload = {
                "op": 1,
                "d": None
            }
            ws.send(json.dumps(heartbeat_payload))
            time.sleep(interval / 1000)  # Convert ms to seconds
    
    # Get heartbeat interval from gateway
    gateway_url = "https://discord.com/api/v9/gateway"
    response = requests.get(gateway_url)
    data = response.json()
    heartbeat_interval = data.get("heartbeat_interval", 45000)
    
    heartbeat_thread = threading.Thread(target=heartbeat, args=(heartbeat_interval,))
    heartbeat_thread.daemon = True
    heartbeat_thread.start()

def get_user_id():
    headers = {
        "Authorization": USER_TOKEN
    }
    
    response = requests.get("https://discord.com/api/v9/users/@me", headers=headers)
    
    if response.status_code == 200:
        return response.json().get("id")
    else:
        print("Failed to get user ID")
        return None

def start_listening():
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp("wss://gateway.discord.gg/?v=9&encoding=json",
                              on_open=on_open,
                              on_message=on_message,
                              on_error=on_error,
                              on_close=on_close)
    
    # Start the inactivity checker thread
    inactive_checker = threading.Thread(target=check_inactive)
    inactive_checker.daemon = True
    inactive_checker.start()
    
    ws.run_forever()

if __name__ == "__main__":
    # First, make sure we can connect to Discord API
    user_id = get_user_id()
    if user_id:
        print(f"Connected as user ID: {user_id}")
        print(f"Monitoring channel ID: {CHANNEL_ID}")
        print("Waiting for messages...")
        prompt = "Generate a random new conversation starter message"
        message = agent.call_agent(prompt)
        send_message(CHANNEL_ID, message)
        start_listening()
    else:
        print("Failed to authenticate. Check your token.")
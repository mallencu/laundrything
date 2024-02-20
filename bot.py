import requests
from slackeventsapi import SlackEventAdapter
from slack_sdk.web import WebClient
import os

slack_signing_secret = os.environ["SLACK_SIGNING_SECRET"]
slack_events_adapter = SlackEventAdapter(slack_signing_secret, "/slack/events")

slack_bot_token = os.environ["SLACK_API_TOKEN"]
slack_client = WebClient(slack_bot_token)

# In-memory data store for laundry machine status
laundry_status = {
    "washing": [0] * 3,  # 3 washing machines
    "drying": [0] * 4,   # 4 drying machines
}

if action.startswith("note_laundry"):
    _, machine_type, machine_number, time_left = action.split()
    machine_number = int(machine_number)
    time_left = int(time_left)
    
if machine_type in laundry_status:
    laundry_status[machine_type][machine_number - 1] = time_left
    response = f"Thank you for noting that you've used {machine_type} machine {machine_number}."
else: response = "Invalid machine type."
    post_message(user_id, response)
elif action == "/laundry_status":
    response = "Laundry Machine Status:\n"
for machine_type, machines in laundry_status.items():
for i, time_left in enumerate(machines, start=1):
    status = "Available" if time_left == 0 else f"In use ({time_left} minutes left)"response += f"{machine_type.capitalize()} Machine {i}: {status}\n"

post_message(payload["channel"]["id"], response)

def post_message(channel, text):
    url = "https://slack.com/api/chat.postMessage"
    headers = {
        "Authorization": f"Bearer {os.environ['SLACK_API_TOKEN']}",
        "Content-Type": "application/json"
    }
    data = {
        "channel": channel,
        "text": text
    }
response = requests.post(url, headers=headers, data=json.dumps(data))
print(response.json())

slack_events_adapter.start(port=5000)

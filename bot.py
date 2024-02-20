import os
import json
import requests
from slackeventsapi import SlackEventAdapter

event_adapter = SlackEventAdapter(os.environ["SLACK_SIGNING_SECRET"], "/slack/events")

laundry_status = {"washing": [0] * 3, "drying": [0] * 4}

def handle_interaction(payload):
    user_id = payload["user"]["id"]
    action = payload["actions"][0]["value"]

    if action.startswith("note_laundry"):
        _, machine_type, machine_number, time_left = action.split()[1:]
        laundry_status[machine_type][int(machine_number) - 1] = int(time_left)
        post_message(user_id, f"Thank you for noting that you've used {machine_type} machine {machine_number}.")

    elif action == "/laundry_status":
        response = "Laundry Machine Status:\n"
        for machine_type, machines in laundry_status.items():
            for i, time_left in enumerate(machines, start=1):
                status = "Available" if time_left == 0 else f"In use ({time_left} minutes left)"
                response += f"{machine_type.capitalize()} Machine {i}: {status}\n"
        post_message(payload["channel"]["id"], response)

def post_message(channel, text):
    url = "https://slack.com/api/chat.postMessage"
    headers = {"Authorization": f"Bearer {os.environ['SLACK_API_TOKEN']}", "Content-Type": "application/json"}
    data = {"channel": channel, "text": text}
    requests.post(url, headers=headers, data=json.dumps(data))

@event_adapter.on("interactive")
def handle_interactive(event_data):
    handle_interaction(json.loads(event_data["payload"]))

if __name__ == "__main__":
    event_adapter.start(port=int(os.environ.get("PORT", 3000)))


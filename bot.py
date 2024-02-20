import os
import json
import requests
from flask import Flask, request

app = Flask(__name__)

# In-memory data store for laundry machine status
laundry_status = {
    "washing": [0] * 3,  # 3 washing machines
    "drying": [0] * 4,   # 4 drying machines
}

# Define route for interactive message actions and commands
@app.route("/interactive", methods=["POST"])
@app.route("/command", methods=["POST"])
def handle_interaction():
    payload = json.loads(request.form["payload"])
    user_id = payload["user"]["id"]
    action = payload["actions"][0]["value"]

    # Handle different actions
    if action.startswith("note_laundry"):
        _, machine_type, machine_number, time_left = action.split()
        machine_number = int(machine_number)
        time_left = int(time_left)

        # Update laundry status
        if machine_type in laundry_status:
            laundry_status[machine_type][machine_number - 1] = time_left
            response = f"Thank you for noting that you've used {machine_type} machine {machine_number}."
        else:
            response = "Invalid machine type."

        # Send response to user
        post_message(user_id, response)

    elif action == "/laundry_status":
        response = "Laundry Machine Status:\n"
        for machine_type, machines in laundry_status.items():
            for i, time_left in enumerate(machines, start=1):
                status = "Available" if time_left == 0 else f"In use ({time_left} minutes left)"
                response += f"{machine_type.capitalize()} Machine {i}: {status}\n"

        # Send response to channel where the command was issued
        post_message(payload["channel"]["id"], response)

    return ""

# Function to send message to Slack
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
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        print(response.json())
    except requests.exceptions.RequestException as e:
        print(f"Error sending message to Slack: {e}")

if __name__ == "__main__":
    # Use dynamic port provided by Heroku, defaulting to 3000 for local development
    port = int(os.environ.get("PORT", 3000))
    app.run(host="0.0.0.0", port=port)

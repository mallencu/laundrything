# Import necessary libraries
import os
from flask import Flask, request
from slack import WebClient
from slackeventsapi import SlackEventAdapter

# Set up Flask app and Slack client
app = Flask(__name__)
slack_token = os.environ["SLACK_API_TOKEN"]
client = WebClient(token=slack_token)
event_adapter = SlackEventAdapter(os.environ["SLACK_SIGNING_SECRET"], "/slack/events")

# Define a route for handling interactive messages
@app.route("/interactive", methods=["POST"])
def handle_interactive():
    # Get the payload from the request
    payload = request.form["payload"]
    # Handle the payload here (e.g., when a user notes their laundry)
    return ""

# Define a message handler for processing incoming messages
@event_adapter.on("message")
def message_handler(event_data):
    message = event_data["event"]
    # Process the message here (e.g., check if it's a command related to laundry)

# Start the Flask app
if __name__ == "__main__":
    app.run(port=3000)

# In-memory data store for laundry machine status
laundry_status = {
    "washing": [0] * 3,  # 3 washing machines
    "drying": [0] * 4,   # 4 drying machines
}

# Define route for interactive message actions
@app.route("/interactive", methods=["POST"])
def handle_interactive():
    payload = request.form["payload"]
    payload_dict = json.loads(payload)
    user_id = payload_dict["user"]["id"]
    action = payload_dict["actions"][0]["value"]

    # Handle different actions
    if action.startswith("note_laundry"):
        # Extract machine type, number, and time left from action
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
        client.chat_postMessage(channel=user_id, text=response)

    return ""

# Define command for displaying laundry status
@app.route("/command", methods=["POST"])
def handle_command():
    data = request.form
    text = data.get("text")
    user_id = data.get("user_id")

    if text == "/laundry_status":
        response = "Laundry Machine Status:\n"
        for machine_type, machines in laundry_status.items():
            for i, time_left in enumerate(machines, start=1):
                status = "Available" if time_left == 0 else f"In use ({time_left} minutes left)"
                response += f"{machine_type.capitalize()} Machine {i}: {status}\n"

        client.chat_postMessage(channel=user_id, text=response)

    return jsonify({"response_type": "in_channel"})

# Start the event listener
if __name__ == "__main__":
    app.run(port=3000)

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

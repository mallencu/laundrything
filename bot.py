import os
import json
from flask import Flask, request, jsonify
import aiohttp
import asyncio
from slackeventsapi import SlackEventAdapter

app = Flask(__name__)
event_adapter = SlackEventAdapter(os.environ["SLACK_SIGNING_SECRET"], "/slack/events")

laundry_status = {
    "washing": [0] * 3,  # 3 washing machines
    "drying": [0] * 4,   # 4 drying machines
}

async def handle_interaction(payload):
    user_id = payload["user"]["id"]
    action = payload["actions"][0]["value"]

    # Handle different actions
    if action.startswith("note_laundry"):
        _, machine_type, machine_number, time_left = action.split()
        machine_number = int(machine_number)
        time_left = int(time_left)
        if machine_type in laundry_status:
            laundry_status[machine_type][machine_number - 1] = time_left
            response = f"Thank you for noting that you've used {machine_type} machine {machine_number}."
        else:
            response = "Invalid machine type."
        await post_message(user_id, response)
    elif action == "/laundry_status":
        response = "Laundry Machine Status:\n"
        for machine_type, machines in laundry_status.items():
            for i, time_left in enumerate(machines, start=1):
                status = "Available" if time_left == 0 else f"In use ({time_left} minutes left)"
                response += f"{machine_type.capitalize()} Machine {i}: {status}\n"
        await post_message(payload["channel"]["id"], response)

async def post_message(channel, text):
    url = "https://slack.com/api/chat.postMessage"
    headers = {
        "Authorization": f"Bearer {os.environ['SLACK_API_TOKEN']}",
        "Content-Type": "application/json"
    }
    data = {
        "channel": channel,
        "text": text
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=data) as response:
            print(await response.json())

@app.route("/slack/events", methods=["POST"])
async def handle_slack_events():
    if request.headers.get("X-Slack-Retry-Reason"):
        return jsonify({"status": "ignored"}), 200

    payload = json.loads(request.data)
    await handle_interaction(payload)
    return jsonify({"status": "received"}), 200

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(event_adapter.start_async())
    app.run(port=int(os.environ.get("PORT", 3000)))

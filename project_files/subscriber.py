import json
import os
import time
import paho.mqtt.client as mqtt
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
MQTT_BROKER = "test.mosquitto.org"
TOPIC_USER_INPUT = "survey/user_input"
TOPIC_AI_RESPONSE = "survey/ai_response"

# Emotion labels mapping
emotion_labels = {
    "A": "Excitement",
    "B": "Uncertainty",
    "C": "Frustration"
}

# Global tracking
has_survey_started = False
completed_emotions = []
selected_emotion = None
previous_responses = []
probe_level = 0  # Tracks progress in the reflection process

# Initialize MQTT Client
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

def on_connect(client, userdata, flags, reason_code, properties=None):
    """Handles connection to MQTT Broker."""
    if reason_code == 0:
        print("Subscriber Connected to MQTT Broker")
        client.subscribe(TOPIC_USER_INPUT)
    else:
        print(f"Connection failed with error code {reason_code}")

def on_message(client, userdata, msg):
    """Handles incoming AI-generated messages and manages response flow."""
    try:
        payload = json.loads(msg.payload.decode())
        print("\nSubscriber received message on", TOPIC_USER_INPUT, ":", payload)

        ai_response = payload.get("ai_response", "")
        selected_emotion = payload.get("emotion_selected")
        previous_responses = payload.get("previous_responses")
        probe_level = payload.get("probe_level")

        if not ai_response:
            print("Error: No question received from AI.")
            return

        print("\nAI-Generated Question:", ai_response)

        # Only allow responses at proper probe levels
        if probe_level in [2, 4, 6]: 
            handle_user_response(probe_level)
        elif probe_level == 7:  # Completion step
            complete_reflection(selected_emotion)

    except json.JSONDecodeError:
        print("Error: Received invalid JSON format.")
    except Exception as e:
        print(f"Error in on_message: {str(e)}")

def setup_survey():
    """Displays the survey introduction and available emotions."""
    print("\nWelcome to your personal reflection survey!")
    print("* First, choose an emotion by entering A, B, or C.")
    print("* Then, the AI will ask you a reflection question.")
    print("* After that, you can type anything you want in response—no need to press another key.")
    print("* You can keep going or press 'F' at any time to finish.")

    print("\nChoose an emotion:")
    for key, emotion in emotion_labels.items():
        print(f"{key} - {emotion}")

def show_progress(probe_level):
    """Displays progress using square blocks to indicate reflection depth."""
    completed_steps = (probe_level) // 2  # Fills square after each user response (levels 2, 4, 6)
    total_steps = 3
    progress_bar = "■" * completed_steps + "▢" * (total_steps - completed_steps)
    print(f"\nProgress: {progress_bar} ({completed_steps}/{total_steps} reflections completed)")

def handle_user_response(probe_level):
    """Handles free-type user responses and tracks probe progression."""
    global selected_emotion, previous_responses

    show_progress(probe_level)  # Show progress before user responds

    user_response = input("\nType your response below (or press 'F' to finish):\n> ").strip()

    if user_response.upper() == "F":
        handle_session_end()
        return

    previous_responses.append(user_response)

    if probe_level == 6:  # If user has completed all three perspectives, finalize the reflection
        complete_reflection(selected_emotion)
        return

    next_probe_level = probe_level + 1
    transmit_user_data(user_response, next_probe_level)

def complete_reflection(selected_emotion):
    """Handles completion logic when probe level 7 is reached."""
    completed_emotions.append(selected_emotion)

    remaining_emotions = [key for key in emotion_labels.keys() if key not in completed_emotions]

    print("\nReflection completed for", emotion_labels[selected_emotion])
    show_progress(7)  # Show 100% completion

    if remaining_emotions:
        print(f"\nYou've reflected on {len(completed_emotions)}/3 emotions.")
        print(f"Choose another emotion: {', '.join(remaining_emotions)} or press 'F' to finish.")
    else:
        print("\nYou've completed reflections for all emotions! Press 'F' to finish.")

def transmit_user_data(user_response, probe_level):
    """Sends user response back to the publisher to generate follow-up questions."""
    payload = json.dumps({
        "input": user_response,
        "emotion_selected": selected_emotion,
        "previous_responses": previous_responses,
        "probe_level": probe_level
    })

    client.publish(TOPIC_AI_RESPONSE, payload)
    print(f"\nPublished user response to {TOPIC_AI_RESPONSE}: {payload}")

def handle_session_end():
    """Ends the session gracefully."""
    print("\nEnding your reflection session. Thank you for participating!")
    client.disconnect()
    exit()

def start_survey():
    """Handles emotion selection and initiates reflection process."""
    global probe_level, selected_emotion, previous_responses, has_survey_started
    setup_survey()
    while True:
        if not has_survey_started:
            user_input = input("\nDraw a card (A, B, C) or press 'F' to finish: ").strip().upper()
            if user_input == "F":
                handle_session_end()

            if user_input in emotion_labels and user_input not in completed_emotions:
                selected_emotion = emotion_labels[user_input]
                print('before transmitting', selected_emotion)
                probe_level = 1  # Reset probe level for new emotion
                previous_responses = []  # Reset response history
                transmit_user_data(user_input, probe_level)
                # TODO: this won't cause new emotion to be asked
                has_survey_started = True
            else:
                print("Oops! Please choose a valid key that you haven’t completed yet.")
        time.sleep(5)  # TODO: remove this to stop survey from resetting!!

# MQTT Setup
client.on_connect = on_connect
client.on_message = on_message

print("Connecting to MQTT Broker...")
client.connect(MQTT_BROKER, 1883, 60)

client.loop_start()
# Start the survey process
start_survey()
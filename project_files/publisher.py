import json
import os
import paho.mqtt.client as mqtt
import google.generativeai as genai
from dotenv import load_dotenv
import random

# Load environment variables
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    print("Error: Missing GEMINI API Key in .env file!")
    exit()

# Configure Gemini AI
genai.configure(api_key=API_KEY)

# MQTT Configuration
MQTT_BROKER = "test.mosquitto.org"
TOPIC_USER_INPUT = "survey/user_input"
TOPIC_AI_RESPONSE = "survey/ai_response"

# Emotion labels mapping
emotion_labels = {
    "A": "Excitement",
    "B": "Uncertainty",
    "C": "Frustration"
}

# Initialize MQTT Client
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

def on_connect(client, userdata, flags, reason_code, properties=None):
    """Handles connection to MQTT Broker."""
    if reason_code == 0:
        print("Publisher Connected to MQTT Broker")
        client.subscribe(TOPIC_AI_RESPONSE)
    else:
        print(f"Connection failed with error code {reason_code}")

def on_message(client, userdata, msg):
    """Handles incoming user responses and generates AI-driven questions."""
    try:
        print(f"\nReceived MQTT Message on {TOPIC_AI_RESPONSE}: {msg.payload.decode()}")

        # Parse JSON payload
        payload = json.loads(msg.payload.decode())

        # Extract relevant information
        user_input = payload.get("input")
        previous_responses = payload.get("previous_responses", [])
        probe_level = payload.get("probe_level")
        selected_emotion = payload.get("emotion_selected", "")

        if not user_input:
            print("Error: Missing 'input' field in received message.")
            return   

        print(f"Processing response for emotion {selected_emotion} at probe level {probe_level}")

        # Generate AI response
        ai_response = generate_ai_response(selected_emotion, previous_responses, probe_level)

        if not ai_response:
            print("Error: AI response was empty.")
            return

        # Increment probe level correctly
        next_probe_level = probe_level + 1 if probe_level < 7 else 7

        # Construct response payload
        response_payload = json.dumps({
            "emotion_selected": selected_emotion,
            "input": user_input,
            "previous_responses": previous_responses + [user_input],
            "probe_level": next_probe_level,
            "ai_response": ai_response
        })

        print(f"AI response published to {TOPIC_USER_INPUT}: {response_payload}")
        client.publish(TOPIC_USER_INPUT, response_payload)

    except json.JSONDecodeError:
        print("Error: Received invalid JSON format.")
    except Exception as e:
        print(f"Error in on_message: {str(e)}")

def generate_ai_response(selected_emotion, previous_responses, probe_level):
    """Generates AI-driven reflection questions based on structured 3-step process."""
    emotion_labels = {
        "A": "Excitement",
        "B": "Uncertainty",
        "C": "Frustration"
    }

    get_emotion = emotion_labels.get(selected_emotion, selected_emotion).lower()
    last_response = previous_responses[-1] if previous_responses else ""
    context_responses = previous_responses[-2:] if len(previous_responses) >= 2 else previous_responses

    # Step 0: Initial Emotion Selection (AI acknowledges selection & asks first follow-up)
    if probe_level == 1:
        return f"You selected {get_emotion}. Let's take a moment to reflect. What happened today that made you feel this way?"

    # Step 1: First AI Follow-Up (Encouraging Storytelling, Builds on User Response)
    if probe_level == 3:
        return random.choice([
            f"That's a great moment to reflect on. When you think about {last_response}, what details stand out the most?",
            f"Can you walk me through what was happening right before {last_response} occurred? What set the stage for it?",
        ])

    # Step 2: Second AI Follow-Up (Deepening Emotional Awareness, Expands Across Responses)
    if probe_level == 5:
        return random.choice([
            f"Thinking about {last_response}, how did it make you feel in the moment? Did those emotions shift as time passed?",
            f"Has a moment like {last_response} happened before in your life? What patterns do you notice in how you experience {get_emotion}?",
        ])

    # Step 3: Mark Emotion as Fully Explored
    if probe_level == 7:
        return "You've completed this reflection. Feel free to explore another emotion or press 'F' to finish."

# Attach MQTT Callbacks BEFORE connecting
client.on_connect = on_connect
client.on_message = on_message

# Connect to MQTT Broker
print("Connecting to MQTT Broker...")
client.connect(MQTT_BROKER, 1883, 60)
print("Successfully connected to MQTT Broker!")

# Start MQTT listening loop
client.loop_forever()
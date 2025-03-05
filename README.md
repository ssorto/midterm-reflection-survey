# Daily Reflection Survey System
**DesignTK 531 Midterm**  
**Author: Stephanie Sorto-Moreno**  

## Overview
The **Daily Reflection Survey System** is an **AI-powered interactive tool** that guides users through structured introspection. By selecting emotions and responding to AI-generated prompts, users engage in meaningful self-reflection while AI deepens their insights.  

The system supports:
- **Conversational prompting** for guided self-reflection
- **A structured three-step user experience**
- **MQTT-based real-time AI interactions**
- **Scalable multi-user session support**

---

## User Experience Flow
The survey consists of **three total user interactions** per emotion:  
1. **Emotion Selection** – User selects an emotion (Excitement, Uncertainty, or Frustration).  
2. **Free Response 1** – AI asks a storytelling-based question, and the user types a response.  
3. **Free Response 2** – AI deepens reflection with a follow-up question, and the user types a final response.  
4. **Reflection Complete** – AI acknowledges completion, and the user can explore another emotion or finish.  

After **all three steps**, the emotion is marked as completed, and the user can **select a new emotion** or **end the survey**.

---

## Technical Architecture
### Code Components
- **`subscriber.py`** – Handles user interaction, publishes responses to MQTT, and receives AI-generated follow-ups.
- **`publisher.py`** – Processes user responses, generates AI prompts, and sends them back to the user.
- **`MQTT Broker`** – Facilitates real-time message exchange between the subscriber (user interface) and publisher (AI processor).

### System Diagram
- User input **(subscriber)** ⟶ Published to MQTT topic ⟶ AI Processing **(publisher)** ⟶ AI-generated prompt ⟶ Sent back to the user.

---

## MQTT Communication
| **Step** | **User Input** | **Publisher Response** |
|----------|--------------|-----------------------|
| **0** | Emotion Selection (A, B, or C) | AI acknowledges choice and generates first question |
| **1** | Free Response 1 | AI prompts storytelling expansion |
| **2** | Free Response 2 | AI deepens emotional awareness |
| **3** | Reflection Complete | AI confirms completion and suggests next steps |

- **Topics Used**:
  - `survey/user_input` – For user responses.
  - `survey/ai_response` – For AI-generated questions.

---

## Features
### Current Implementation
✔ **Three-step structured reflection**  
✔ **Progress tracking via square indicators (■▢▢ format)**  
✔ **AI-generated open-ended, conversational prompts**  
✔ **MQTT-based real-time message exchange**  

### Scalability
- **Multi-user session tracking**  
- **Customizable daily topics**  
- **Voice input for interaction**  

---

## Setup & Execution
### 1. Install Dependencies
Ensure you have Python 3 and the required libraries installed:

```sh
pip install paho-mqtt google-generativeai python-dotenv
```

### 2. Set Up API Key
Store your **Google Gemini API key** in a `.env` file:

```sh
GEMINI_API_KEY=your_api_key_here
```

### 3. Run the Application
- Start the **publisher** (AI response generator):
  ```sh
  python3 publisher.py
  ```
- Start the **subscriber** (User interaction):
  ```sh
  python3 subscriber.py
  ```

---

## Presentation Summary
The **DesignTK 531 Midterm** presentation covers:
- **Demo of user interaction and AI prompting**
- **AI Prompting Logic**:
  1. **Emotion Selection** – Acknowledges user’s choice.
  2. **Storytelling Prompt** – Encourages elaboration.
  3. **Deepening Reflection** – Expands emotional awareness.
  4. **Reflection Completed** – Marks emotion as finished.
- **System Scalability & Future Improvements**
  - Supporting **multi-user sessions**
  - Expanding interaction to **voice-based reflection**
  - Adding **customizable reflection topics**

---



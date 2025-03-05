import json
import os
import pandas as pd
from datetime import datetime

# Define results directory and ensure it exists
RESULTS_DIR = "results"
if not os.path.exists(RESULTS_DIR):
    os.makedirs(RESULTS_DIR)

# Define file paths
DATA_FILE = os.path.join(RESULTS_DIR, "survey_responses.json")

# Generate a timestamped file name for the Excel export
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
EXCEL_FILE = os.path.join(RESULTS_DIR, f"UXR_analysis_{timestamp}.xlsx")

def save_response(user_input, selected_emotion, ai_followup, probe_level):
    """
    Saves both user responses and AI-generated questions into a JSON file for analysis.
    """
    response_data = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "selected_emotion": selected_emotion,
        "user_response": user_input,
        "ai_followup_question": ai_followup,
        "probe_level": probe_level
    }

    # Append to JSON file
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r+", encoding="utf-8") as f:
            existing_data = json.load(f)
            existing_data.append(response_data)
            f.seek(0)
            json.dump(existing_data, f, indent=4)
    else:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump([response_data], f, indent=4)

    print(f"\nResponse saved successfully in {DATA_FILE}")

def json_to_excel():
    """
    Converts JSON survey responses to an Excel file for analysis.
    """
    if not os.path.exists(DATA_FILE):
        print(f"\nNo survey response data found in {DATA_FILE}. Run the survey first.")
        return

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        if not data:
            print("\nJSON file is empty. No responses to export.")
            return

        # Convert JSON to DataFrame
        df = pd.DataFrame(data)

        # Reorder columns for better readability
        column_order = [
            "timestamp", "selected_emotion", "user_response", 
            "ai_followup_question", "probe_level"
        ]
        df = df[column_order]

        # Export to Excel
        df.to_excel(EXCEL_FILE, index=False, engine="openpyxl")

        print(f"\nData successfully exported to {EXCEL_FILE}")

    except Exception as e:
        print(f"\nError exporting JSON to Excel: {e}")

# Example Usage
if __name__ == "__main__":
    json_to_excel()

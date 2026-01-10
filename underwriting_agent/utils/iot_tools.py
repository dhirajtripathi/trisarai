from langchain_core.tools import tool
import random

# Mock Data
MOCK_EHR = {
    "user123": [
        {"date": "2015-05-20", "condition": "Fractured Radius (Arm)", "status": "Resolved"},
        {"date": "2023-11-10", "condition": "Hypertension", "status": "Active"},
        {"date": "2024-01-15", "condition": "Seasonal Allergies", "status": "Active"}
    ],
    "user456": [
         {"date": "2020-02-01", "condition": "Type 2 Diabetes", "status": "Active"},
         {"date": "2022-08-15", "condition": "Appendectomy", "status": "Resolved"}
    ]
}

MOCK_WEARABLES = {
    "user123": {
        "avg_daily_steps": 8500,
        "resting_heart_rate": 72,
        "sleep_quality_score": 78
    },
    "user456": {
        "avg_daily_steps": 3200,
        "resting_heart_rate": 85,
        "sleep_quality_score": 60
    }
}

@tool
def fetch_ehr(user_id: str) -> list:
    """
    Retrieves Electronic Health Records (EHR) for a given user.
    """
    return MOCK_EHR.get(user_id, [])

@tool
def fetch_wearable_data(user_id: str) -> dict:
    """
    Retrieves real-time wearable device data (steps, heart rate, sleep).
    """
    return MOCK_WEARABLES.get(user_id, {
        "avg_daily_steps": 5000,
        "resting_heart_rate": 75,
        "sleep_quality_score": 70
    })

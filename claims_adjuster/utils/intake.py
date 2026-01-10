from typing import Dict, Any, Optional

def analyze_multimodal_input(image_status: str, voice_transcript: str) -> Dict[str, Any]:
    """
    Simulates a Multi-Modal LLM analysis.
    
    Args:
        image_status: "clear" or "blurry" (Simulated input from UI)
        voice_transcript: Text transcript of the user's voice note.
        
    Returns:
        Structured dictionary with analysis results or quality error.
    """
    
    # 1. Quality Check
    if image_status == "blurry":
        return {
            "is_valid": False,
            "error_reason": "Image Quality Error: The provided photo is too blurry to detect damage. Please submit a clearer photo.",
            "damage_detected": None
        }
    
    # 2. Damage Extraction (Simulation)
    damage_type = "unknown"
    if "glass" in voice_transcript.lower() or "windshield" in voice_transcript.lower():
        damage_type = "windshield"
    elif "bumper" in voice_transcript.lower():
        damage_type = "bumper"
    elif "off-road" in voice_transcript.lower():
        damage_type = "suspension" # Hint at exclusion
    
    return {
        "is_valid": True,
        "damage_detected": damage_type,
        "confidence": 0.95,
        "summary": f"Visual analysis confirms damage to {damage_type}. Voice note corroborates the incident."
    }

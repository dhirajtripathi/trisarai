from langchain_core.tools import tool
import random
import hashlib

# Mock Database of "Known Bad Actors"
GHOST_BROKERS = {
    "john_doe_fake": "Red Flag: Linked to large scale ghost broking ring in 2024.",
    "premium_scam_ltd": "Red Flag: Known for issuing fake policy documents."
}

# Mock "Recycled Photo" Database (using hash of description for simulation)
RECYCLED_PHOTOS_DB = [
    "kitchen_fire_001", "car_crash_front_bumper_02"
]

@tool
def check_social_media(name: str, claim_date: str) -> str:
    """
    Scans public social media for posts by the claimant around the claim date.
    Returns a summary of relevant activity.
    """
    # Simulation logic
    if "party" in name.lower():
        return f"Found post on {claim_date}: 'Best party ever! House looks great!' (Contradicts fire claim)"
    elif "travel" in name.lower():
        return f"Found post on {claim_date}: Checked in at 'Bahamas Resort'. (Claimant stated they were home)"
    else:
        return "No relevant public activity found near claim date."

@tool
def check_ghost_broking_db(entity_name: str) -> str:
    """
    Checks the entity against an internal Ghost Broking blacklist.
    """
    key = entity_name.lower().replace(" ", "_")
    result = GHOST_BROKERS.get(key)
    if result:
        return f"MATCH FOUND in Ghost Broking DB: {result}"
    return "No match found in Ghost Broking watchlist."

@tool
def analyze_claim_photo(photo_description: str) -> str:
    """
    Simulates visual analysis of a claim photo to detect anomalies or recycling.
    Input should be a description of the photo (e.g., 'kitchen_fire_001').
    """
    # In a real app, this would hash the image file.
    # Here we simulate by checking the description string against a list.
    if photo_description.lower() in RECYCLED_PHOTOS_DB:
        return f"CRITICAL: Image '{photo_description}' matches a photo used in 3 previous claims (Claim IDs: #902, #331, #112). Possible Recycled Photo Fraud."
    
    if "photoshop" in photo_description.lower():
        return "Metadata Warning: Image EXIF data indicates editing with Adobe Photoshop."
        
    return "Image analysis passed. No metadata anomalies or recycling detected."

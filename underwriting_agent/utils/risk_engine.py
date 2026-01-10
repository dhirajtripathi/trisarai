from datetime import datetime

def analyze_risk(medical_history: list, wearable_data: dict) -> dict:
    """
    Filters irrelevant history and calculates risk score.
    
    Logic:
    1. Filter out Resolved conditions older than 2 years.
    2. Analyze Active conditions.
    3. Use Wearable data to adjust score.
    """
    current_year = datetime.now().year
    relevant_conditions = []
    
    for record in medical_history:
        year = int(record['date'].split('-')[0])
        is_recent = (current_year - year) <= 2
        
        # Keep if Active OR Recent
        if record['status'] == 'Active' or is_recent:
            relevant_conditions.append(record)
            
    # Base Score logic (Lower is better)
    base_score = 100
    
    # Penalties for conditions
    for cond in relevant_conditions:
        if cond['condition'] == 'Hypertension': base_score -= 15
        elif cond['condition'] == 'Type 2 Diabetes': base_score -= 20
        elif cond['status'] == 'Active': base_score -= 5
        
    # Bonus for Wearables
    steps = wearable_data.get('avg_daily_steps', 0)
    if steps > 8000: base_score += 10
    elif steps > 5000: base_score += 5
    
    # Suggest Nudges
    nudges = []
    if steps < 8000:
        nudges.append("Increase daily steps to 8k for 5% discount.")
    if any(c['condition'] == 'Hypertension' for c in relevant_conditions):
        nudges.append("Enroll in DASH diet program for 10% discount.")
        
    # Premium Calculation
    premium = 500 - (base_score * 2) # Arbitrary formula
    if premium < 100: premium = 100 # Floor
    
    return {
        "risk_score": base_score,
        "relevant_conditions": relevant_conditions,
        "suggested_premium": round(premium, 2),
        "nudges": nudges,
        "reasoning": f"Base Score impacted by {len(relevant_conditions)} relevant conditions. Wearable bonus applies."
    }

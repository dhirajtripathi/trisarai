from langchain_core.tools import tool

# Mock Database for Parts
PARTS_DB = {
    "windshield": 350.00,
    "bumper": 450.00,
    "headlight": 200.00,
    "side_mirror": 150.00
}

LABOR_RATES = {
    "default": 85.00, # Per hour
    "glass_specialist": 60.00
}

@tool
def get_part_price(part_name: str) -> float:
    """
    Retrieves the current market price for a vehicle part.
    """
    normalized = part_name.lower().strip() 
    return PARTS_DB.get(normalized, 100.00) # Default fallback

@tool
def get_labor_rate(work_type: str = "default") -> float:
    """
    Retrieves the standard labor rate per hour for the type of work.
    """
    return LABOR_RATES.get(work_type, 85.00)

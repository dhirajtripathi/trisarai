from data_models import CustomerProfile, LifeEvent, EndorsementProposal

def calculate_pricing(customer: CustomerProfile, event: LifeEvent) -> EndorsementProposal:
    """
    Deterministic pricing logic based on life events.
    In a real system, this would call a rating engine API.
    """
    base_premium = customer.annual_premium
    
    if event.event_type == "Marriage":
        # Marriage often lowers auto risk but suggests Life Insurance
        if "Life" not in customer.existing_policies:
            premium_change = 600.00
            return EndorsementProposal(
                policy_type="Life",
                recommended_action="Add Term Life Policy",
                premium_change=premium_change,
                reasoning="Marriage brings shared financial responsibilities. A term life policy ensures your spouse is protected.",
                new_total_premium=base_premium + premium_change
            )
        else:
             # Discount on Auto
            premium_change = -150.00
            return EndorsementProposal(
                policy_type="Auto",
                recommended_action="Apply Marriage Discount",
                premium_change=premium_change,
                reasoning="Congratulations! Married drivers statistically have fewer accidents, qualifying you for a discount.",
                new_total_premium=base_premium + premium_change
            )

    elif event.event_type == "New Home":
        # Needs Homeowners, maybe bundle with Auto
        premium_change = 1200.00
        return EndorsementProposal(
            policy_type="Homeowners",
            recommended_action="Add Homeowners Policy",
            premium_change=premium_change,
            reasoning="Purchasing a home requires specific coverage structure/property protection that Renters insurance doesn't cover.",
            new_total_premium=base_premium + premium_change
        )
        
    elif event.event_type == "New Car":
        premium_change = 800.00
        return EndorsementProposal(
            policy_type="Auto",
            recommended_action="Update Auto Policy",
            premium_change=premium_change,
            reasoning="Newer vehicles have higher replacement costs, requiring adjusted collision and comprehensive limits.",
            new_total_premium=base_premium + premium_change
        )
    
    else:
        return EndorsementProposal(
            policy_type="General",
            recommended_action="Review Coverage",
            premium_change=0.0,
            reasoning="Periodic review suggested based on recent activity.",
            new_total_premium=base_premium
        )

def calculate_credit_score(data):
    """
    Calculates an alternative credit score based on form data.
    This is our "MTS Generation" logic.
    Score range: 300 - 850
    """
    # Base score
    score = 300
    
    # Component scores (out of 100)
    payment_history_score = 0
    financial_stability_score = 0
    credit_utilization_score = 0
    data_richness_score = 50 # Base score for providing data

    try:
        # --- 1. Payment History (Rent & Utilities) ---
        # Weight: 35%
        history_map = {"excellent": 100, "good": 75, "fair": 40, "poor": 10}
        rent_history = history_map.get(data.get('rentHistory'), 0)
        utility_history = history_map.get(data.get('utilityHistory'), 0)
        payment_history_score = int((rent_history * 0.6) + (utility_history * 0.4))
        score += payment_history_score * 1.5 # 1.5 * 100 = 150 points

        # --- 2. Financial Stability (Income, Savings, Employment) ---
        # Weight: 30%
        income = float(data.get('monthlyIncome', 0))
        avg_balance = float(data.get('avgBalance', 0))
        savings_rate = float(data.get('savingsRate', 0))
        overdrafts = int(data.get('overdrafts', 0))
        stability_map = {"high": 100, "medium": 70, "low": 30}
        emp_stability = stability_map.get(data.get('employmentStability'), 0)
        
        stability_score = 0
        if avg_balance > 1000: stability_score += 25
        if savings_rate > 0.1: stability_score += 25
        if overdrafts == 0: stability_score += 25
        if emp_stability > 50: stability_score += 25
        financial_stability_score = stability_score
        score += financial_stability_score * 1.65 # 1.65 * 100 = 165 points

        # --- 3. Credit Utilization (Income vs. Rent) ---
        # Weight: 15%
        rent = float(data.get('rentAmount', 0))
        utilization_score = 0
        if income > 0:
            rent_to_income = rent / income
            if rent_to_income < 0.3: utilization_score = 100
            elif rent_to_income < 0.4: utilization_score = 70
            elif rent_to_income < 0.5: utilization_score = 40
            else: utilization_score = 10
        credit_utilization_score = utilization_score
        score += utilization_score * 0.8 # 0.8 * 100 = 80 points
        
        # --- 4. Data Richness ---
        # Weight: ~5% (plus base score)
        data_richness_score = 70 # Give a fixed score for filling the form
        score += data_richness_score * 0.55 # 0.55 * 100 = 55 points
        
        # Total points available: 150 + 165 + 80 + 55 = 450
        # Base score 300 + 450 = 750. Oh, let's adjust.
        # Max score is 850. 850 - 300 = 550 points to distribute.
        # Let's re-weight:
        # Pay History (35% of 550): 192.5 pts -> 1.925 * score
        # Stability (30% of 550): 165 pts -> 1.65 * score
        # Utilization (15% of 550): 82.5 pts -> 0.825 * score
        # Richness (20% of 550): 110 pts -> 1.1 * score
        # Let's redo the score math...
        
        score = 300
        score += payment_history_score * 1.925
        score += financial_stability_score * 1.65
        score += credit_utilization_score * 0.825
        score += data_richness_score * 1.1 # Give 1.1 * 70 = 77 points

        # Final score clamping (300-850)
        final_score = max(300, min(850, int(score)))

        # Determine rating
        if final_score >= 800: rating = "Excellent"
        elif final_score >= 740: rating = "Very Good"
        elif final_score >= 670: rating = "Good"
        elif final_score >= 580: rating = "Fair"
        else: rating = "Poor"

        return {
            "total_score": final_score,
            "rating": rating,
            "trend": "▲ +5 pts vs. last month", # Dummy trend data
            "breakdown": {
                "payment_history": {"score": payment_history_score, "label": "Payment History"},
                "financial_stability": {"score": financial_stability_score, "label": "Financial Stability"},
                "credit_utilization": {"score": credit_utilization_score, "label": "Income-to-Rent"},
                "data_richness": {"score": data_richness_score, "label": "Data Richness"},
            }
        }
    except Exception as e:
        print(f"Error in scoring engine: {e}")
        # Return a default "error" score
        return {
            "total_score": 400,
            "rating": "Error",
            "trend": "...",
            "breakdown": {
                "payment_history": {"score": 0, "label": "Payment History"},
                "financial_stability": {"score": 0, "label": "Financial Stability"},
                "credit_utilization": {"score": 0, "label": "Income-to-Rent"},
                "data_richness": {"score": 0, "label": "Data Richness"},
            }
        }
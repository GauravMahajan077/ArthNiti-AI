# health_monitor.py - New file for health monitoring logic

def calculate_health_metrics(user_data, current_score):
    """
    Calculates various health indicators.
    """
    # Health Grade based on score
    if current_score >= 800:
        grade = "A+"
    elif current_score >= 740:
        grade = "A"
    elif current_score >= 670:
        grade = "B+"
    elif current_score >= 580:
        grade = "B"
    else:
        grade = "C"
    
    # Risk Level calculation
    overdrafts = int(user_data.get('overdrafts', 0))
    savings_rate = float(user_data.get('savingsRate', 0))
    
    if overdrafts == 0 and savings_rate >= 0.15:
        risk = "LOW"
    elif overdrafts <= 2 and savings_rate >= 0.10:
        risk = "MEDIUM"
    else:
        risk = "HIGH"
    
    # Trend (mock - in real app, compare with historical data)
    trend = "+15"  # You'd calculate this from DB
    
    return {
        "grade": grade,
        "risk_level": risk,
        "trend": trend,
        "current_score": current_score
    }


def generate_90day_roadmap(current_score, health_data):
    """
    Generates personalized 90-day improvement plan.
    """
    roadmap = {
        "phase1": {
            "title": "Days 1-30: Build Foundation",
            "actions": [],
            "target_gain": 10
        },
        "phase2": {
            "title": "Days 31-60: Optimize Habits", 
            "actions": [],
            "target_gain": 15
        },
        "phase3": {
            "title": "Days 61-90: Reach Excellence",
            "actions": [],
            "target_gain": 20
        }
    }
    
    # Customize based on health data
    if health_data['risk_level'] == "HIGH":
        roadmap['phase1']['actions'] = [
            "Eliminate all overdrafts",
            "Pay all bills on time",
            "Build emergency fund of ₹5000"
        ]
    else:
        roadmap['phase1']['actions'] = [
            "Maintain payment streak",
            "Increase savings by 5%",
            "Review budget allocations"
        ]
    
    roadmap['phase2']['actions'] = [
        "Increase savings rate to 20%",
        "Maintain zero overdrafts for 60 days",
        "Improve employment stability documentation"
    ]
    
    roadmap['phase3']['actions'] = [
        "Build 3-month emergency fund",
        "Diversify income sources",
        "Achieve 750+ credit score"
    ]
    
    return roadmap


def generate_change_recommendation(predicted_score):
    """
    Generates recommendation based on score change.
    """
    score = predicted_score['total_score']
    
    if score >= 800:
        return {
            "message": "Excellent! You're in the top tier. Maintain these habits.",
            "priority": "maintain",
            "emoji": "🎉"
        }
    elif score >= 740:
        return {
            "message": "Very good! Small tweaks can push you to excellent.",
            "priority": "optimize",
            "emoji": "👍"
        }
    else:
        return {
            "message": "Focus on the key factors: payments, savings, and stability.",
            "priority": "improve",
            "emoji": "💪"
        }
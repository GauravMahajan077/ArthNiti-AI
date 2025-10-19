import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import google.generativeai as genai
from datetime import datetime, timedelta
import requests  # ✅ FIX: Use proper requests library

# --- Local Imports ---
from scoring_engine import calculate_credit_score
from ai_agents import get_ai_analysis, get_loan_suggestion, get_dummy_ai_data

# --- Single, Centralized Configuration Block ---
load_dotenv()
model = None

try:
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("--- WARNING: GOOGLE_API_KEY not found. AI features will use dummy data. ---")
    else:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(
            model_name='gemini-2.0-flash-exp',
            generation_config={"response_mime_type": "application/json"}
        )
        print("--- Gemini client configured successfully. ---")
except Exception as e:
    print(f"--- ERROR initializing Gemini client: {e}. AI features will use dummy data. ---")
    model = None

# --- Flask App Initialization ---
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-change-in-prod')

# ✅ FIX: Proper CORS configuration for OAuth with sessions
CORS(app, 
     supports_credentials=True,
     origins=['http://localhost:5500', 'http://127.0.0.1:5500', 'http://localhost:3000', 'http://127.0.0.1:3000'],
     allow_headers=['Content-Type'],
     expose_headers=['Set-Cookie'],
     methods=['GET', 'POST', 'OPTIONS'])


# ===== HELPER FUNCTIONS FOR HEALTH MONITOR =====

def calculate_health_metrics(user_data, current_score):
    """Calculates various health indicators."""
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
    
    overdrafts = int(user_data.get('overdrafts', 0))
    savings_rate = float(user_data.get('savingsRate', 0))
    
    if overdrafts == 0 and savings_rate >= 0.15:
        risk = "LOW"
    elif overdrafts <= 2 and savings_rate >= 0.10:
        risk = "MEDIUM"
    else:
        risk = "HIGH"
    
    trend = "+15"
    
    return {
        "grade": grade,
        "risk_level": risk,
        "trend": trend,
        "current_score": current_score
    }


def generate_90day_roadmap(current_score, health_data):
    """Generates personalized 90-day improvement plan."""
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
    """Generates recommendation based on score change."""
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


def get_health_insights(model, health_data):
    """Gets AI-powered health insights. Falls back to dummy data if model unavailable."""
    if not model:
        return {
            "insights": [
                "Your credit health is being monitored",
                "Continue good financial habits",
                "Check back regularly for updates"
            ]
        }
    
    try:
        prompt = f"""
        You are a financial health advisor. Based on this health data:
        - Health Grade: {health_data['grade']}
        - Risk Level: {health_data['risk_level']}
        - Current Score: {health_data['current_score']}
        - Trend: {health_data['trend']}
        
        Provide 3 short, actionable health insights in JSON format:
        {{
          "insights": [
            "First insight about their current status",
            "Second insight about what to watch out for",
            "Third insight with a quick win suggestion"
          ]
        }}
        """
        
        response = model.generate_content(prompt)
        import json
        return json.loads(response.text)
        
    except Exception as e:
        print(f"Error getting health insights: {e}")
        return {
            "insights": [
                f"Your credit health grade is {health_data['grade']}",
                f"Current risk level: {health_data['risk_level']}",
                "Keep monitoring your financial habits for improvements"
            ]
        }


def get_personalized_finance_insight(model, user_data):
    """Uses Gemini to generate personalized financial insights"""
    if not model:
        return {
            "insight_en": "Keep tracking your bills to maintain good financial health.",
            "insight_hi": "अच्छे वित्तीय स्वास्थ्य के लिए अपने बिलों पर नज़र रखें।"
        }
    
    try:
        prompt = f"""
        Based on this user's financial data:
        - Monthly Income: ₹{user_data.get('monthly_income', 30000)}
        - Current Balance: ₹{user_data.get('current_balance', 2500)}
        - Upcoming Bills: ₹{user_data.get('upcoming_bills', 13449)}
        - Payment Streak: {user_data.get('streak', 47)} days
        - Budget Usage: {user_data.get('budget_usage', 68)}%
        
        Generate a short, actionable financial insight in both English and Hindi.
        Format as JSON:
        {{
          "insight_en": "English insight here",
          "insight_hi": "Hindi insight here"
        }}
        """
        
        response = model.generate_content(prompt)
        import json
        return json.loads(response.text)
    
    except Exception as e:
        print(f"Error generating personalized insight: {e}")
        return {
            "insight_en": "Keep tracking your bills to maintain good financial health.",
            "insight_hi": "अच्छे वित्तीय स्वास्थ्य के लिए अपने बिलों पर नज़र रखें।"
        }


# ===== MAIN API ROUTES =====

@app.route('/api/score', methods=['POST'])
def get_score_route():
    """Main score calculation endpoint."""
    try:
        data = request.get_json()
        print("Data received for /api/score:", data)

        score_data = calculate_credit_score(data)
        print("Calculated Score:", score_data)

        ai_data = get_ai_analysis(model, score_data['total_score'], score_data['breakdown'], data)
        print("AI Analysis Result:", ai_data)

        full_response = {
            "score": score_data,
            "ai_analysis": ai_data
        }
        return jsonify(full_response)

    except Exception as e:
        print(f"--- FATAL ERROR in /api/score route: {e}")
        return jsonify({
            "error": "Failed to process score request on the server.",
            "score": None,
            "ai_analysis": get_dummy_ai_data()
        }), 500


@app.route('/api/suggest_loan', methods=['POST'])
def suggest_loan_route():
    """Loan suggestion endpoint."""
    try:
        request_data = request.get_json()
        score = request_data.get('score')
        user_data = request_data.get('userData')

        if not score or not user_data:
            print("--- ERROR: Missing score or userData in /api/suggest_loan request.")
            return jsonify({"suggestion": {"error": "Missing required data from frontend."}}), 400

        print(f"Loan suggestion requested for score: {score}")

        loan_suggestion = get_loan_suggestion(model, score, user_data)
        print("Loan Suggestion Result:", loan_suggestion)

        return jsonify({
            "suggestion": loan_suggestion
        })

    except Exception as e:
        print(f"--- FATAL ERROR in /api/suggest_loan route: {e}")
        return jsonify({"suggestion": {"error": "Server error while generating loan suggestion."}}), 500


@app.route('/api/health-monitor', methods=['POST'])
def health_monitor_route():
    """Returns financial health data and predictions."""
    try:
        request_data = request.get_json()
        user_data = request_data.get('userData')
        current_score = request_data.get('currentScore', 720)
        
        print(f"Health monitor requested for score: {current_score}")
        
        health_data = calculate_health_metrics(user_data, current_score)
        ai_insights = get_health_insights(model, health_data)
        roadmap = generate_90day_roadmap(current_score, health_data)
        
        return jsonify({
            "health_metrics": health_data,
            "ai_insights": ai_insights,
            "roadmap": roadmap
        })
        
    except Exception as e:
        print(f"--- ERROR in /api/health-monitor: {e}")
        return jsonify({"error": "Failed to generate health data"}), 500


@app.route('/api/predict-score', methods=['POST'])
def predict_score_route():
    """Predicts score based on what-if scenarios."""
    try:
        simulation_data = request.get_json()
        print("Simulation data received:", simulation_data)
        
        predicted_score = calculate_credit_score(simulation_data)
        recommendation = generate_change_recommendation(predicted_score)
        
        return jsonify({
            "predicted_score": predicted_score['total_score'],
            "breakdown": predicted_score['breakdown'],
            "recommendation": recommendation
        })
        
    except Exception as e:
        print(f"--- ERROR in /api/predict-score: {e}")
        return jsonify({"error": "Prediction failed"}), 500


# ===== FINANCE ROUTES =====

@app.route('/api/finance/bills', methods=['GET', 'POST'])
def manage_bills():
    """GET: Retrieve user's bills, POST: Add new bill"""
    if request.method == 'GET':
        sample_bills = [
            {
                "id": "bill_1",
                "name": "Rent Payment",
                "name_hi": "किराया",
                "amount": 12000,
                "due_date": "2025-10-25",
                "status": "pending",
                "category": "rent",
                "recurring": True
            },
            {
                "id": "bill_2",
                "name": "Electricity",
                "name_hi": "बिजली",
                "amount": 850,
                "due_date": "2025-10-15",
                "status": "paid",
                "category": "utilities",
                "recurring": True
            },
            {
                "id": "bill_3",
                "name": "Internet",
                "name_hi": "इंटरनेट",
                "amount": 599,
                "due_date": "2025-10-10",
                "status": "overdue",
                "category": "services",
                "recurring": True
            }
        ]
        return jsonify({"bills": sample_bills})
    
    elif request.method == 'POST':
        bill_data = request.get_json()
        return jsonify({
            "success": True,
            "message": "Bill added successfully",
            "bill_id": "bill_new_123"
        })


@app.route('/api/finance/reminders', methods=['GET'])
def get_smart_reminders():
    """Returns AI-generated smart reminders based on payment patterns"""
    try:
        user_id = request.args.get('user_id', 'demo_user')
        
        reminders = [
            {
                "id": "rem_1",
                "type": "upcoming",
                "priority": "medium",
                "message_en": "Rent due in 6 days. Your usual payment day is approaching.",
                "message_hi": "किराया 6 दिन में देय है।",
                "icon": "💸",
                "action": "snooze"
            },
            {
                "id": "rem_2",
                "type": "overdue",
                "priority": "high",
                "message_en": "Internet bill overdue! Pay now to maintain streak.",
                "message_hi": "इंटरनेट बिल अतिदेय!",
                "icon": "🚨",
                "action": "pay_now"
            },
            {
                "id": "rem_3",
                "type": "ai_tip",
                "priority": "low",
                "message_en": "AI Tip: Pay electricity before Oct 22 to avoid late fee",
                "message_hi": "सुझाव: बिजली बिल 22 अक्टूबर से पहले दें",
                "icon": "💡",
                "action": "got_it"
            }
        ]
        
        return jsonify({"reminders": reminders})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/finance/streak', methods=['GET'])
def get_payment_streak():
    """Returns current payment streak and achievements"""
    try:
        streak_data = {
            "current_streak": 47,
            "best_streak": 89,
            "total_on_time_payments": 156,
            "achievements": [
                {
                    "id": "ach_1",
                    "name": "7 Day Hero",
                    "name_hi": "7 दिन का हीरो",
                    "icon": "🏆",
                    "unlocked": True,
                    "unlocked_date": "2025-09-01"
                },
                {
                    "id": "ach_2",
                    "name": "30 Day Master",
                    "name_hi": "30 दिन का मास्टर",
                    "icon": "⭐",
                    "unlocked": True,
                    "unlocked_date": "2025-09-24"
                },
                {
                    "id": "ach_3",
                    "name": "100 Day Legend",
                    "name_hi": "100 दिन का लीजेंड",
                    "icon": "💎",
                    "unlocked": False,
                    "progress": 47
                },
                {
                    "id": "ach_4",
                    "name": "365 Day King",
                    "name_hi": "365 दिन का राजा",
                    "icon": "👑",
                    "unlocked": False,
                    "progress": 47
                }
            ]
        }
        
        return jsonify(streak_data)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/finance/budget', methods=['GET', 'POST'])
def manage_budget():
    """GET: Get current budget status, POST: Update budget"""
    if request.method == 'GET':
        budget_data = {
            "total_budget": 30000,
            "spent": 20400,
            "remaining": 9600,
            "percentage_used": 68,
            "categories": {
                "rent": {"spent": 12000, "budget": 15000},
                "utilities": {"spent": 1449, "budget": 2000},
                "food": {"spent": 4500, "budget": 6000},
                "entertainment": {"spent": 2451, "budget": 3000}
            },
            "ai_insight_en": "You're on track! At this rate, you'll save ₹5,000 this month.",
            "ai_insight_hi": "आप सही दिशा में हैं! इस गति से आप ₹5,000 बचाएंगे।",
            "projection": {
                "expected_savings": 5000,
                "days_until_next_paycheck": 6
            }
        }
        
        return jsonify(budget_data)
    
    elif request.method == 'POST':
        budget_updates = request.get_json()
        return jsonify({
            "success": True,
            "message": "Budget updated successfully"
        })


@app.route('/api/finance/emergency-shield', methods=['GET'])
def check_emergency_shield():
    """Predicts overdraft risk using AI"""
    try:
        current_balance = 2500
        upcoming_bills = 13449
        
        risk_ratio = current_balance / upcoming_bills
        
        if risk_ratio < 1.1:
            status = "warning"
            message_en = "Your account balance is low. Consider postponing non-essential expenses."
            message_hi = "आपका खाता बैलेंस कम है। गैर-जरूरी खर्चों को टालें।"
            risk_score = 85
        elif risk_ratio < 1.5:
            status = "caution"
            message_en = "Monitor your balance closely. Some bills are approaching."
            message_hi = "अपने बैलेंस पर नज़र रखें।"
            risk_score = 45
        else:
            status = "safe"
            message_en = "No overdraft risk detected in next 7 days"
            message_hi = "अगले 7 दिनों में कोई जोखिम नहीं"
            risk_score = 10
        
        return jsonify({
            "status": status,
            "risk_score": risk_score,
            "current_balance": current_balance,
            "upcoming_bills": upcoming_bills,
            "message_en": message_en,
            "message_hi": message_hi,
            "next_check": "2025-10-20T09:00:00",
            "alert_method": "SMS + App Notification"
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/finance/ai-learning-status', methods=['GET'])
def get_ai_learning_status():
    """Returns how much the AI has learned about user's patterns"""
    try:
        learning_status = {
            "payment_pattern_accuracy": 87,
            "spending_behavior_accuracy": 92,
            "data_points_collected": 247,
            "months_analyzed": 3,
            "confidence_level": "high",
            "message_en": "AI has learned your habits after analyzing 3 months of data. Predictions are now highly accurate.",
            "message_hi": "AI ने 3 महीने के डेटा का विश्लेषण करके आपकी आदतें सीख ली हैं।"
        }
        
        return jsonify(learning_status)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/finance/mark-paid', methods=['POST'])
def mark_bill_paid():
    """Marks a bill as paid and updates streak"""
    try:
        data = request.get_json()
        bill_id = data.get('bill_id')
        
        return jsonify({
            "success": True,
            "message": "Bill marked as paid",
            "new_streak": 48,
            "achievement_unlocked": None
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ===== GAME ROUTES =====

@app.route('/api/game/challenges', methods=['GET'])
def get_game_challenges():
    """Returns game challenges for Credit Clash."""
    try:
        real_score = request.args.get('realScore', 720)
        user_data_str = request.args.get('userData', '{}')
        import json
        user_data = json.loads(user_data_str)
        
        challenges = [
            {
                "id": "challenge_1",
                "title": "Payment Streak Challenge",
                "description": "Maintain 5 consecutive on-time payments",
                "difficulty": "easy",
                "reward": 50,
                "category": "payments",
                "personalized": f"Based on your {user_data.get('rentHistory', 'fair')} rent history"
            },
            {
                "id": "challenge_2",
                "title": "Savings Boost",
                "description": "Save 10% of your income this week",
                "difficulty": "medium",
                "reward": 75,
                "category": "savings",
                "personalized": f"Target: ₹{int(float(user_data.get('monthlyIncome', 4500)) * 0.10)}"
            },
            {
                "id": "challenge_3",
                "title": "Overdraft Dodge",
                "description": "Avoid any overdrafts for 7 days",
                "difficulty": "hard",
                "reward": 100,
                "category": "stability",
                "personalized": f"You've had {user_data.get('overdrafts', 0)} overdrafts recently"
            }
        ]
        
        if int(real_score) > 750:
            for challenge in challenges:
                challenge['difficulty'] = 'easy' if challenge['difficulty'] == 'medium' else challenge['difficulty']
        
        return jsonify({
            "challenges": challenges,
            "player_score": int(real_score),
            "level": "Beginner" if int(real_score) < 600 else "Intermediate" if int(real_score) < 750 else "Expert"
        })
    
    except Exception as e:
        print(f"--- ERROR in /api/game/challenges: {e}")
        return jsonify({"error": "Failed to load challenges"}), 500


@app.route('/api/game/submit-score', methods=['POST'])
def submit_game_score():
    """Submits game score and calculates real score impact."""
    try:
        data = request.get_json()
        game_score = data.get('gameScore', 0)
        real_score = data.get('realScore', 720)
        user_data = data.get('userData', {})
        
        score_boost = min(game_score // 10, 50)
        new_real_score = min(real_score + score_boost, 850)
        
        return jsonify({
            "success": True,
            "game_score": game_score,
            "score_boost": score_boost,
            "new_real_score": new_real_score,
            "message": f"Great game! You've earned a {score_boost} point boost to your real score.",
            "achievement": "Game Master" if game_score > 800 else None
        })
    
    except Exception as e:
        print(f"--- ERROR in /api/game/submit-score: {e}")
        return jsonify({"error": "Failed to submit score"}), 500


# ===== HEALTH CHECK ENDPOINT =====

@app.route('/api/health', methods=['GET'])
def health_check():
    """Simple health check endpoint to verify server is running."""
    return jsonify({
        "status": "healthy",
        "ai_available": model is not None,
        "endpoints": [
            "/api/score",
            "/api/suggest_loan",
            "/api/health-monitor",
            "/api/predict-score",
            "/api/finance/bills",
            "/api/finance/reminders",
            "/api/finance/streak",
            "/api/finance/budget",
            "/api/finance/emergency-shield",
            "/api/finance/ai-learning-status",
            "/api/finance/mark-paid",
            "/api/game/challenges",
            "/api/game/submit-score"
        ]
    })


# ===== START SERVER =====

if __name__ == '__main__':
    print("\n" + "="*50)
    print("🚀 ArthNiti Backend Server Starting...")
    print("="*50)
    print(f"✅ AI Model Status: {'Active' if model else 'Offline (using dummy data)'}")
    print(f"📡 Frontend URL: http://localhost:5500")
    print(f"📡 Backend URL: http://localhost:5000")
    print("\n📡 Available endpoints:")
    print("   ├─ POST /api/score")
    print("   ├─ POST /api/suggest_loan")
    print("   ├─ POST /api/health-monitor")
    print("   ├─ POST /api/predict-score")
    print("   ├─ GET  /api/finance/* (bills, reminders, streak, etc.)")
    print("   └─ GET  /api/game/* (challenges, submit-score)")
    print("="*50 + "\n")
    
    app.run
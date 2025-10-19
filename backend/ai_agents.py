import os
import json
import google.generativeai as genai

# NOTE: Configuration is now done in app.py and the 'model' object is passed in.

def get_ai_analysis(model, score, breakdown, data):
    """
    Calls Google Gemini (if available) to get analysis and recommendations.
    Accepts the configured 'model' object.
    """
    if not model:
        print("--- Gemini model not available in get_ai_analysis. Returning dummy data. ---")
        return get_dummy_ai_data() # Fallback if model failed to init in app.py

    # Create profile summary (Keep as is)
    profile_summary = f"""
    - User's Final Score: {score}
    - Score Breakdown: {json.dumps(breakdown, indent=2)}
    - User's Raw Data: {json.dumps(data, indent=2)}
    """

    # System Prompt (Keep as is)
    prompt = """
    You are "ArthNiti AI", an expert, friendly, and encouraging financial analyst for the Indian market.
    Your user has just received an alternative credit score.
    Your task is to provide:
    1.  **Insights**: 3 short (one-sentence) bullet points explaining *why* they got their score. Be specific.
    2.  **Recommendations**: 3 actionable recommendations to improve their score.

    You MUST return your answer in a specific JSON format. Do not write any other text.
    The JSON format MUST be:
    {
      "insights": [
        "Your insight here. (e.g., Your 'excellent' rent history is strongly boosting your score!)",
        "Your second insight here. (e.g., Your low 'overdrafts' show great financial stability.)",
        "Your third insight here. (e.g., Your 'rent-to-income' ratio is a bit high, which is holding your score back.)"
      ],
      "recommendations": [
        {
          "title": "Short Rec Title (e.g., 'Boost Your Savings')",
          "priority": "High",
          "impact": "High",
          "difficulty": "Medium"
        },
        {
          "title": "Short Rec Title 2 (e.g., 'Maintain On-Time Utility Bills')",
          "priority": "Medium",
          "impact": "Medium",
          "difficulty": "Low"
        },
        {
          "title": "Short Rec Title 3 (e.g., 'Improve Employment Stability')",
          "priority": "Low",
          "impact": "Low",
          "difficulty": "Low"
        }
      ]
    }

    Analyze this financial profile and provide the required JSON output:
    """ + profile_summary

    try:
        print("--- Calling Gemini for AI Analysis...")
        response = model.generate_content(prompt)
        print("--- Gemini AI Analysis call successful.")
        ai_response_json = json.loads(response.text)
        return ai_response_json

    except Exception as e:
        print(f"--- ERROR calling Gemini API for Analysis: {e}")
        print("--- Falling back to dummy AI data.")
        return get_dummy_ai_data() # Consistent fallback

def get_loan_suggestion(model, score, data):
    """
    Calls Google Gemini (if available) to suggest a loan amount and terms.
    Accepts the configured 'model' object.
    """
    if not model:
        print("--- Gemini model not available in get_loan_suggestion. Returning error suggestion. ---")
        return {"error": "AI Agent offline"} # Fallback if model failed to init

    # Create profile summary (Keep as is)
    profile_summary = f"""
    - User's ArthNiti Score: {score}
    - Monthly Income: {data.get('monthlyIncome', 'N/A')}
    - Monthly Rent: {data.get('rentAmount', 'N/A')}
    - Average Bank Balance: {data.get('avgBalance', 'N/A')}
    - Employment Stability: {data.get('employmentStability', 'N/A')}
    """

    # Loan Prompt (Keep as is)
    loan_prompt = f"""
    You are "ArthNiti AI Loan Advisor". Based on the user's alternative credit score and basic financial data, suggest a *single, small, safe* personal loan amount they might qualify for. Consider their score, income vs rent, and stability. Keep amounts conservative (e.g., INR 5000-25000). Also suggest a simple term (e.g., 3 months, 6 months).

    You MUST return your answer in this exact JSON format:
    {{
      "suggested_amount_inr": <number>,
      "suggested_term_months": <number>,
      "reasoning": "Short explanation (e.g., Based on your good score and stable income...)"
    }}

    Analyze this profile for a loan suggestion:
    {profile_summary}
    """

    try:
        print("--- Calling Gemini for Loan Suggestion...")
        response = model.generate_content(loan_prompt)
        print("--- Gemini Loan Suggestion call successful.")
        loan_suggestion = json.loads(response.text)
        return loan_suggestion

    except Exception as e:
        print(f"--- ERROR calling Gemini API for Loan Suggestion: {e}")
        return {"error": "Could not determine loan suggestion"} # Consistent error structure

# Centralized Dummy Data Function
def get_dummy_ai_data():
    """ Returns placeholder data if the API fails or is not configured. """
    print("--- Providing Dummy AI Data ---") # Log when dummy data is used
    return {
      "insights": [
        "Insight generation requires a valid API key.",
        "Ensure your GOOGLE_API_KEY is set in the .env file.",
        "This is placeholder data."
      ],
      "recommendations": [
        {
          "title": "Check API Key Setup",
          "priority": "High",
          "impact": "High",
          "difficulty": "Low"
        },
        {
          "title": "Review Backend Logs",
          "priority": "Medium",
          "impact": "Medium",
          "difficulty": "Low"
        },
        {
          "title": "Consult Documentation",
          "priority": "Low",
          "impact": "Low",
          "difficulty": "Low"
        }
      ]
    }
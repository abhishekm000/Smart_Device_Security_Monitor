import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Configure API Key if it exists
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY and GEMINI_API_KEY != "YOUR_API_KEY_HERE":
    genai.configure(api_key=GEMINI_API_KEY)

def generate_threat_report(alert_dict):
    """Generates a natural language threat report using Gemini"""
    if not GEMINI_API_KEY or GEMINI_API_KEY == "YOUR_API_KEY_HERE":
        return "ERROR: Gemini API Key not configured. Please add your key to the .env file."

    prompt = f"""
    You are an expert Cybersecurity AI Analyst responding to a network intrusion alert.
    Analyze the following IoT device network alert and provide a short, professional, 3-sentence mitigation strategy for the network administrator.

    Alert Details:
    - Threat Type: {alert_dict.get('prediction')}
    - Risk Level: {alert_dict.get('risk_level')} (Score: {alert_dict.get('risk_score')})
    - Target Device ID: {alert_dict.get('device_id')}
    - Source IP: {alert_dict.get('source_ip')}
    - Model Confidence: {alert_dict.get('confidence')}

    Format your response in plain text. Do not use markdown. Keep it urgent and actionable.
    """

    try:
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"AI Analysis Failed: {str(e)}"

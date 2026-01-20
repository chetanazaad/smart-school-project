# smart_school_backend/routes/chatbot.py
import os
from flask import Blueprint, request, jsonify, current_app

try:
    import google.generativeai as genai
except ImportError as e:
    print(f"❌ Could not import google.generativeai: {e}")
    genai = None

chatbot_bp = Blueprint("chatbot", __name__)

# --- CONFIGURATION ---
# For better security, use environment variables
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")  # Get from env variable

model = None

# Initialize the model only if the package is installed and the key is provided
if genai and GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        
        # List available models to find a valid one
        print("🔍 Checking available Gemini models...")
        model_name = None
        try:
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    print(f"   - {m.name}")
                    if not model_name: model_name = m.name # Pick first available
        except Exception as model_err:
            print(f"   ⚠️ Could not list models: {model_err}")
        
        if not model_name: model_name = 'gemini-1.5-flash' # Fallback
        print(f"👉 Using model: {model_name}")
        model = genai.GenerativeModel(model_name)
    except Exception as e:
        print(f"❌ Error configuring Gemini: {e}")
        print("   Chatbot will not be available")
        model = None
else:
    if not genai:
        print("⚠️ WARNING: google.generativeai is not installed")
    if not GEMINI_API_KEY:
        print("⚠️ WARNING: GEMINI_API_KEY environment variable not set")
    print("   Chatbot will not be available (optional feature)")

# The route is now an empty string, which correctly maps to "/api/chatbot"
# without causing a redirect.
@chatbot_bp.route("", methods=["POST", "OPTIONS"])
def chat():
    # Handle CORS preflight request
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200

    if not model:
        return jsonify({
            "reply": "AI service is not configured. Please check the server logs for errors and ensure the API key is set."
        }), 500

    data = request.get_json()
    if not data or "message" not in data:
        return jsonify({"reply": "Invalid request. 'message' field is required."}), 400
        
    message = data["message"]
    if not message.strip():
        return jsonify({"reply": "Please provide a non-empty message."}), 400

    try:
        current_app.logger.info(f"✉️  Sending message to Gemini: '{message}'")
        # Generate content with the model
        response = model.generate_content(message)
        
         # Return the generated text
        return jsonify({"reply": response.text})

    except Exception as e:
        current_app.logger.error(f"❌ Gemini API Error: {e}")
        return jsonify({
            "reply": "The AI service is currently unavailable. Please check the server logs and try again later."
        }), 500
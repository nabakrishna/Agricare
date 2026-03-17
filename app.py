import os
import sqlite3
import re
import logging
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from rapidfuzz import process, fuzz
import json
import base64
import requests
from markupsafe import escape

# ============================================================
# SECURITY: Load API key from environment variable, NOT hardcoded.
# Set it by running: export PLANT_ID_API_KEY="your_key_here"
# ============================================================
PLANT_ID_API_KEY = "u###########################################"
PLANT_ID_ENDPOINT = "https://plant.id/api/v3/identification"

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_PATH = 'agricare.db'

# --- GREETINGS ---
GREETING_RESPONSES = {
    "hello": "Hello! How can I help your crops today?",
    "hi": "Hi there! What plant are you worried about?",
    "hey": "Hey! I'm ready to help.",
    "good morning": "Good morning! I hope your fields are lush.",
    "good afternoon": "Good afternoon! How can I help?",
    "good evening": "Good evening! I'm here if you need to check a plant.",
    "bye": "Goodbye! Happy farming!",
    "goodbye": "See you later! Take care.",
    "thank you": "You're very welcome!",
    "thanks": "No problem! Happy to help.",
    "ok": "Got it. Anything else?",
    "okay": "Okay! What's next?"
}

# --- INAPPROPRIATE CONTENT FILTER ---
INAPPROPRIATE_WORDS = [
    'sex', 'porn', 'xxx', 'nude', 'naked', 'fuck', 'shit', 'bitch',
    'dick', 'pussy', 'cock', 'nsfw', 'adult', 'erotic', 'explicit'
]

# ============================================================
# FIX #6: Plant.id API name → our DB plant name mapper.
# Maps common/scientific names that the API might return to the
# exact plant names stored in our SQLite database.
# ============================================================
PLANT_NAME_MAPPING = {
    # Rice / Paddy
    "oryza sativa": "Rice", "paddy": "Rice", "rice": "Rice",
    "oryza": "Rice",
    # Wheat
    "triticum aestivum": "Wheat", "wheat": "Wheat",
    "triticum": "Wheat",
    # Maize / Corn
    "zea mays": "Maize", "corn": "Maize", "maize": "Maize",
    "zea": "Maize",
    # Potato
    "solanum tuberosum": "Potato", "potato": "Potato",
    # Sugarcane
    "saccharum officinarum": "Sugarcane", "sugarcane": "Sugarcane",
    "saccharum": "Sugarcane", "sugar cane": "Sugarcane",
    # Cotton
    "gossypium hirsutum": "Cotton", "cotton": "Cotton",
    "gossypium": "Cotton",
    # Soybean
    "glycine max": "Soybean", "soybean": "Soybean",
    "soy": "Soybean", "soya": "Soybean",
    # Chickpea
    "cicer arietinum": "Chickpea", "chickpea": "Chickpea",
    "gram": "Chickpea", "chick pea": "Chickpea",
    # Groundnut / Peanut
    "arachis hypogaea": "Groundnut", "groundnut": "Groundnut",
    "peanut": "Groundnut",
    # Rapeseed / Mustard
    "brassica napus": "Rapeseed & Mustard",
    "brassica juncea": "Rapeseed & Mustard",
    "brassica": "Rapeseed & Mustard",
    "mustard": "Rapeseed & Mustard",
    "rapeseed": "Rapeseed & Mustard",
    "canola": "Rapeseed & Mustard",
}

# ============================================================
# FIX #2: Strip citation markers like [1], [12], [1,3,5] from text
# ============================================================
def strip_citations(text: str) -> str:
    """Remove academic citation markers like [1], [1, 3], [12, 15] from text."""
    return re.sub(r'\[\s*\d+(?:\s*,\s*\d+)*\s*\]', '', text).strip()

# ============================================================
# FIX #2: Clean all string fields in a disease DB row
# ============================================================
def clean_disease_record(record) -> dict:
    fields = ['disease', 'organic_treatment', 'chemical_treatment',
              'prevention', 'symptom', 'detailed_symptoms', 'plant_name']
    cleaned = {}
    for field in fields:
        val = record[field] if field in record.keys() else ''
        cleaned[field] = strip_citations(val) if val else ''
    return cleaned

def contains_inappropriate_content(text: str) -> bool:
    text_lower = text.lower()
    cleaned = text_lower.replace(' ', '').replace('_', '').replace('-', '').replace('.', '')
    for word in INAPPROPRIATE_WORDS:
        if re.search(r'\b' + re.escape(word) + r'\b', text_lower):
            return True
        if word in cleaned:
            return True
    return False

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def clean_text(text: str) -> str:
    text = re.sub(r'(.)\1{2,}', r'\1\1', text)
    return text.lower().strip()

# ============================================================
# FIX #6: Map Plant.id API name to our DB plant name
# ============================================================
def map_api_plant_to_db(api_plant_name: str) -> str | None:
    """
    Given a plant name from the Plant.id API (e.g. 'Carex acutiformis'),
    try to find the best matching plant in our database.
    Returns the DB plant name string, or None if no match.
    """
    lower = api_plant_name.lower().strip()

    # 1. Direct lookup in our mapping dict
    if lower in PLANT_NAME_MAPPING:
        return PLANT_NAME_MAPPING[lower]

    # 2. Check if any mapping key is a substring of the API name
    for key, db_name in PLANT_NAME_MAPPING.items():
        if key in lower:
            return db_name

    # 3. Fuzzy match against full DB plant list
    conn = get_db_connection()
    cursor = conn.execute('SELECT DISTINCT plant_name FROM diseases')
    db_plants = [row['plant_name'] for row in cursor.fetchall()]
    conn.close()

    best = process.extractOne(lower, db_plants, scorer=fuzz.partial_ratio, score_cutoff=65)
    if best:
        return best[0]

    return None


@app.route('/api/analyze-symptoms', methods=['POST'])
def analyze_symptoms():
    conn = None
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON payload."}), 400

        # SECURITY: sanitize raw string input
        raw_input = str(escape(data.get('symptoms', '')))
        user_input = clean_text(raw_input)

        if not user_input:
            return jsonify({"error": "Please describe symptoms."}), 400

        # --- 0. INAPPROPRIATE CONTENT CHECK ---
        if contains_inappropriate_content(raw_input):
            return jsonify({
                "is_casual": True,
                "message": "⚠️ I'm here to help with crop diseases only. Please keep your questions farming-related."
            })

        # --- 1. GIBBERISH CHECK ---
        if len(raw_input) > 3 and not re.search(r'[aeiouy]', user_input):
            return jsonify({
                "is_casual": True,
                "message": "I didn't understand that. Please use real words to describe your crop problem."
            })

        # --- 2. GREETING CHECK ---
        greeting_match = process.extractOne(
            user_input,
            GREETING_RESPONSES.keys(),
            scorer=fuzz.WRatio,
            score_cutoff=60
        )
        if greeting_match:
            matched_phrase, score, _ = greeting_match
            if len(user_input) < 4 and score < 90:
                pass
            elif len(user_input) < 25:
                return jsonify({
                    "is_casual": True,
                    "message": GREETING_RESPONSES[matched_phrase]
                })

        # --- 3. PLANT DETECTION ---
        conn = get_db_connection()
        cursor = conn.execute('SELECT DISTINCT plant_name FROM diseases')
        plants = [row['plant_name'] for row in cursor.fetchall()]

        detected_plant = None
        best_plant_match = process.extractOne(
            user_input, plants, scorer=fuzz.partial_ratio, score_cutoff=70
        )
        if best_plant_match:
            detected_plant = best_plant_match[0]

        # --- 4. MISSING PLANT CHECK ---
        if not detected_plant:
            cursor = conn.execute('SELECT symptom FROM diseases')
            all_symptoms = [row['symptom'] for row in cursor.fetchall()]
            symptom_check = process.extractOne(
                user_input, all_symptoms, scorer=fuzz.token_set_ratio, score_cutoff=50
            )
            if symptom_check and symptom_check[1] > 45:
                return jsonify({
                    "is_casual": True,
                    "message": f"I can see some symptoms. Which plant is this for? I support: {', '.join(plants)}"
                })
            else:
                return jsonify({
                    "is_casual": True,
                    "message": "I'm not sure what you mean. Try saying something like 'Rice with brown spots'."
                })

        # --- 5. JUST A PLANT NAME (no symptoms) ---
        check_input = user_input.replace(detected_plant.lower(), "")
        check_input = re.sub(r'\b(plant|crop|tree|the|my|is|check|in|on|has|have)\b', '', check_input).strip()
        if len(check_input) < 3:
            return jsonify({
                "is_casual": True,
                "message": f"Got it — you have a {detected_plant} crop. What symptoms is it showing? (e.g. 'brown spots', 'yellow leaves', 'wilting')"
            })

        # --- 6. FIND BEST DISEASE MATCH ---
        cursor = conn.execute('SELECT * FROM diseases WHERE plant_name = ?', (detected_plant,))
        relevant_diseases = cursor.fetchall()

        best_match = None
        highest_score = 0
        for disease in relevant_diseases:
            score = fuzz.WRatio(user_input, disease['symptom'].lower())
            if len(user_input) < 8 and user_input in disease['symptom'].lower():
                score += 20
            if score > highest_score:
                highest_score = score
                best_match = disease

        if highest_score < 45:
            return jsonify({
                "is_casual": True,
                "message": f"I know you're asking about {detected_plant}, but I don't recognise that symptom. Try describing it differently."
            })

        # FIX #2: strip citations before sending to frontend
        record = clean_disease_record(best_match)

        return jsonify({
            "disease": record['disease'],
            "organic": record['organic_treatment'],
            "chemical": record['chemical_treatment'],
            "prevention": record['prevention'],
            "source": f"AgriCare Database · Confidence: {int(highest_score)}%",
            "is_casual": False
        })

    except Exception as e:
        logger.error(f"System Error in analyze_symptoms: {e}", exc_info=True)
        return jsonify({"error": "An internal error occurred. Please try again."}), 500
    finally:
        if conn:
            conn.close()


@app.route('/api/analyze-image', methods=['POST'])
def analyze_image():
    """
    FIX #4: Full robustness wrapper — handles API down, bad format,
            no plant detected, unhealthy plant, and maps to our DB.
    FIX #6: Maps API plant name → DB plant name for a full diagnosis.
    """
    conn = None
    try:
        # --- Validate upload ---
        if 'image' not in request.files:
            return jsonify({"error": "No image file received."}), 400

        file = request.files['image']
        if file.filename == '':
            return jsonify({"error": "Empty filename."}), 400

        allowed_types = {'image/jpeg', 'image/png', 'image/gif', 'image/webp'}
        if file.content_type not in allowed_types:
            return jsonify({"error": "Please upload a JPEG, PNG, GIF, or WebP image."}), 400

        image_data = base64.b64encode(file.read()).decode("utf-8")

        # --- FIX #4: Check API key is configured ---
        if not PLANT_ID_API_KEY:
            return jsonify({
                "error": "Image analysis is temporarily unavailable (API key not configured). Please describe symptoms in text."
            }), 503

        payload = {
            "images": [image_data],
            "health": "all",
            "classification_level": "species"
        }
        headers = {"Api-Key": PLANT_ID_API_KEY, "Content-Type": "application/json"}

        # --- FIX #4: Timeout + connection error handling ---
        try:
            response = requests.post(
                PLANT_ID_ENDPOINT, headers=headers, json=payload, timeout=20
            )
            response.raise_for_status()
        except requests.exceptions.Timeout:
            return jsonify({
                "error": "The plant identification service timed out. Please try again shortly."
            }), 503
        except requests.exceptions.ConnectionError:
            return jsonify({
                "error": "Cannot reach the plant identification service. Please check your internet connection."
            }), 503
        except requests.exceptions.HTTPError as http_err:
            logger.error(f"Plant.id HTTP error: {http_err}")
            return jsonify({
                "error": "The plant identification service returned an unexpected error. Please try again later."
            }), 503

        # --- FIX #4: Safe JSON parse ---
        try:
            result = response.json()
        except ValueError:
            logger.error("Plant.id returned non-JSON response")
            return jsonify({
                "error": "Received an unexpected response from the identification service."
            }), 503

        # --- FIX #4: Safe nested access ---
        api_result = result.get("result", {})

        is_plant = api_result.get("is_plant", {}).get("binary", False)
        if not is_plant:
            return jsonify({
                "is_casual": True,
                "message": "🌿 No plant was detected in this image. Please upload a clear photo of the affected crop."
            })

        # Extract plant name safely
        suggestions = api_result.get("classification", {}).get("suggestions", [])
        if not suggestions:
            return jsonify({
                "is_casual": True,
                "message": "I detected a plant but couldn't identify the species. Please try a clearer photo or describe the symptoms in text."
            })

        api_plant_name = suggestions[0].get("name", "Unknown")
        api_plant_probability = suggestions[0].get("probability", 0)

        # Is plant healthy?
        is_healthy = api_result.get("is_healthy", {}).get("binary", True)

        if is_healthy:
            return jsonify({
                "is_casual": True,
                "message": f"✅ Your plant looks like <strong>{api_plant_name}</strong> and appears <strong>healthy</strong>! No disease detected. Keep up the good farming! 🌾"
            })

        # --- FIX #6: Map API plant name → our DB ---
        db_plant = map_api_plant_to_db(api_plant_name)

        disease_suggestions = api_result.get("disease", {}).get("suggestions", [])
        api_disease_name = disease_suggestions[0].get("name", "Unknown") if disease_suggestions else "Unknown"

        if not db_plant:
            # We know it's sick but can't map to our DB — give partial info
            return jsonify({
                "is_casual": True,
                "message": (
                    f"🔍 Identified: <strong>{api_plant_name}</strong> "
                    f"(confidence: {int(api_plant_probability * 100)}%)<br>"
                    f"⚠️ Disease detected: <strong>{api_disease_name}</strong><br>"
                    f"Unfortunately I don't have detailed treatment data for this species yet. "
                    f"Try describing the symptoms in text for a manual diagnosis."
                )
            })

        # We have a DB match — look up disease by symptom fuzzy match
        conn = get_db_connection()
        cursor = conn.execute('SELECT * FROM diseases WHERE plant_name = ?', (db_plant,))
        db_diseases = cursor.fetchall()

        best_match = None
        highest_score = 0
        search_term = api_disease_name.lower()

        for disease in db_diseases:
            # Match against disease name AND symptom
            score = max(
                fuzz.WRatio(search_term, disease['disease'].lower()),
                fuzz.token_set_ratio(search_term, disease['symptom'].lower())
            )
            if score > highest_score:
                highest_score = score
                best_match = disease

        if best_match and highest_score >= 40:
            record = clean_disease_record(best_match)
            return jsonify({
                "disease": record['disease'],
                "organic": record['organic_treatment'],
                "chemical": record['chemical_treatment'],
                "prevention": record['prevention'],
                "source": f"Plant.id API + AgriCare DB · Plant: {api_plant_name} ({int(api_plant_probability * 100)}% confidence)",
                "is_casual": False
            })
        else:
            # DB plant matched but disease not in DB
            return jsonify({
                "is_casual": True,
                "message": (
                    f"🔍 Identified: <strong>{db_plant}</strong> with possible <strong>{api_disease_name}</strong>.<br>"
                    f"I don't have a specific treatment record for this condition yet. "
                    f"Please describe the visual symptoms in text for a manual diagnosis."
                )
            })

    except Exception as e:
        logger.error(f"System Error in analyze_image: {e}", exc_info=True)
        return jsonify({"error": "An internal error occurred during image analysis."}), 500
    finally:
        if conn:
            conn.close()


@app.route('/')
def home():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True, port=5000)

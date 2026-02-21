import os
import sqlite3
import re
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from rapidfuzz import process, fuzz

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
#also have to add mmore restriction word
#def restricted_word():

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# --- TEXT CLEANER ---
def clean_text(text):
    # Reduces repeated chars: "helooooo" -> "heloo"
    text = re.sub(r'(.)\1{2,}', r'\1\1', text)
    return text.lower().strip()

@app.route('/api/analyze-symptoms', methods=['POST'])
def analyze_symptoms():
    conn = None
    try:
        data = request.get_json()
        raw_input = data.get('symptoms', '')
        user_input = clean_text(raw_input)
        
        if not user_input:
            return jsonify({"error": "Please describe symptoms."}), 400

        # --- 1. GIBBERISH CHECK ---
        # Checks for inputs with no vowels (like "hhhh", "vvvv")
        # We check the original raw_input length to catch "hhhhh" before it becomes "hh"
        if len(raw_input) > 3 and not re.search(r'[aeiouy]', user_input):
             return jsonify({
                "is_casual": True,
                "message": "I didn't understand that. Please use real words."
            })
            

        # --- 2. GREETING CHECK (FIXED) ---
        greeting_match = process.extractOne(
            user_input, 
            GREETING_RESPONSES.keys(), 
            scorer=fuzz.WRatio, 
            score_cutoff=60  # Allow slight misspellings like "googd"
        )
        
        # FIX: Increased length limit from 10 to 20 so "good morning" passes
        if greeting_match:
            matched_phrase, score, _ = greeting_match
            # Still prevent short words like "rice" matching "hi", 
            # but allow longer greetings like "good morning" to pass easily
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
            user_input, 
            plants, 
            scorer=fuzz.partial_ratio, 
            score_cutoff=70
        )

        if best_plant_match:
            detected_plant = best_plant_match[0]

        # --- 4. STRICT MISSING PLANT CHECK (FIXED LOGIC) ---
        if not detected_plant:
            # We scan all symptoms to see if the user actually described a disease
            cursor = conn.execute('SELECT symptom FROM diseases')
            all_symptoms = [row['symptom'] for row in cursor.fetchall()]
            
            symptom_check = process.extractOne(
                user_input,
                all_symptoms,
                scorer=fuzz.token_set_ratio,
                score_cutoff=50
            )
            
            # FIX: If the score is low (< 45), it's probably nonsense/illogical, NOT a symptom.
            if symptom_check and symptom_check[1] > 45:
                return jsonify({
                    "is_casual": True,
                    "message": f"I see you mentioned '{user_input}'. Which plant is this for? (I know: {', '.join(plants)})"
                })
            else:
                # This catches things like "table", "computer", or random words
                return jsonify({
                    "is_casual": True,
                    "message": "I'm not sure what you mean. Please say 'Hello', name a crop, or describe a symptom."
                })

        # --- 5. "JUST A PLANT" CHECK ---
        # If user only said "Rice" (no symptoms), ask for details
        check_input = user_input.replace(detected_plant.lower(), "")
        check_input = re.sub(r'\b(plant|crop|tree|the|my|is|check|in|on|has|have)\b', '', check_input).strip()
        
        if len(check_input) < 3:
             return jsonify({
                "is_casual": True,
                "message": f"Okay, I see you have a {detected_plant} crop. What symptoms is it showing? (e.g., 'brown spots' or 'yellow leaves')"
            })

        # --- 6. FIND DISEASE ---
        cursor = conn.execute('SELECT * FROM diseases WHERE plant_name = ?', (detected_plant,))
        relevant_diseases = cursor.fetchall()
        
        best_match = None
        highest_score = 0
        
        for disease in relevant_diseases:
            # WRatio handles typos well
            score = fuzz.WRatio(user_input, disease['symptom'].lower())
            
            # Boost score if the input is a short exact match found inside the text
            if len(user_input) < 8 and user_input in disease['symptom'].lower():
                score += 20 

            if score > highest_score:
                highest_score = score
                best_match = disease

        # Threshold check
        if highest_score < 45:
            return jsonify({
                "is_casual": True,
                "message": f"I know you're asking about {detected_plant}, but I don't recognize that symptom. Could you describe it differently?"
            })

        return jsonify({
            "disease": best_match['disease'],
            "organic": best_match['organic_treatment'],
            "chemical": best_match['chemical_treatment'],
            "prevention": best_match['prevention'],
            "source": f"AgriCare Database (Match: {int(highest_score)}%)",
            "is_casual": False
        })

    except Exception as e:
        logger.error(f"System Error: {e}")
        return jsonify({"error": "An internal error occurred."}), 500
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
    




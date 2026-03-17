-- =========================================================
-- AGRICARE DATABASE SCHEMA (SQLite)
-- For your Flask + SQLite Plant Disease Chatbot
-- =========================================================

PRAGMA foreign_keys = ON;

-- =========================================================
-- 1. DISEASE MASTER TABLE
-- Main knowledge base used by /api/analyze-symptoms
-- =========================================================
CREATE TABLE IF NOT EXISTS diseases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plant_name TEXT NOT NULL,
    disease TEXT NOT NULL,
    symptom TEXT NOT NULL,
    detailed_symptoms TEXT,
    organic_treatment TEXT,
    chemical_treatment TEXT,
    prevention TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Helpful index for faster plant lookup
CREATE INDEX IF NOT EXISTS idx_diseases_plant_name ON diseases(plant_name);
CREATE INDEX IF NOT EXISTS idx_diseases_disease ON diseases(disease);

-- =========================================================
-- 2. USER SESSIONS TABLE
-- Track each user/browser session (optional but professional)
-- =========================================================
CREATE TABLE IF NOT EXISTS user_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT UNIQUE NOT NULL,
    ip_address TEXT,
    user_agent TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_active_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_user_sessions_session_id ON user_sessions(session_id);

-- =========================================================
-- 3. CHAT LOGS TABLE
-- Store every text message + bot response
-- =========================================================
CREATE TABLE IF NOT EXISTS chat_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT,
    user_message TEXT NOT NULL,
    cleaned_message TEXT,
    detected_plant TEXT,
    detected_disease TEXT,
    confidence_score REAL,
    is_casual INTEGER DEFAULT 0, -- 0 = disease result, 1 = greeting/casual/help
    bot_response TEXT,
    response_type TEXT, -- greeting / disease / clarification / error / inappropriate
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES user_sessions(session_id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_chat_logs_session_id ON chat_logs(session_id);
CREATE INDEX IF NOT EXISTS idx_chat_logs_detected_plant ON chat_logs(detected_plant);
CREATE INDEX IF NOT EXISTS idx_chat_logs_created_at ON chat_logs(created_at);

-- =========================================================
-- 4. IMAGE ANALYSIS LOGS
-- Store Plant.id image detection requests/results
-- =========================================================
CREATE TABLE IF NOT EXISTS image_analysis_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT,
    original_filename TEXT,
    file_size_bytes INTEGER,
    mime_type TEXT,
    detected_plant TEXT,
    detected_disease TEXT,
    is_healthy INTEGER, -- 1 = healthy, 0 = diseased, NULL = unknown
    access_token TEXT,
    plant_id_status_code INTEGER,
    raw_api_response TEXT, -- store full JSON response if needed
    bot_message TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES user_sessions(session_id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_image_logs_session_id ON image_analysis_logs(session_id);
CREATE INDEX IF NOT EXISTS idx_image_logs_detected_plant ON image_analysis_logs(detected_plant);
CREATE INDEX IF NOT EXISTS idx_image_logs_created_at ON image_analysis_logs(created_at);

-- =========================================================
-- 5. API REQUEST LOGS
-- Track all API calls made by your Flask backend
-- =========================================================
CREATE TABLE IF NOT EXISTS api_request_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT,
    endpoint TEXT NOT NULL,                 -- /api/analyze-symptoms or /api/analyze-image
    method TEXT NOT NULL,                   -- POST / GET
    request_payload TEXT,                   -- JSON or simplified text
    response_payload TEXT,                  -- JSON response
    status_code INTEGER,
    processing_time_ms REAL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES user_sessions(session_id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_api_logs_endpoint ON api_request_logs(endpoint);
CREATE INDEX IF NOT EXISTS idx_api_logs_created_at ON api_request_logs(created_at);

-- =========================================================
-- 6. ERROR LOGS TABLE
-- Save backend exceptions and debugging data
-- =========================================================
CREATE TABLE IF NOT EXISTS error_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT,
    endpoint TEXT,
    error_type TEXT,
    error_message TEXT,
    stack_trace TEXT,
    request_data TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES user_sessions(session_id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_error_logs_created_at ON error_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_error_logs_endpoint ON error_logs(endpoint);

-- =========================================================
-- 7. INAPPROPRIATE CONTENT LOGS
-- Store blocked content attempts
-- =========================================================
CREATE TABLE IF NOT EXISTS inappropriate_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT,
    user_message TEXT NOT NULL,
    detected_word TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES user_sessions(session_id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_inappropriate_logs_created_at ON inappropriate_logs(created_at);

-- =========================================================
-- 8. FEEDBACK TABLE (OPTIONAL BUT VERY USEFUL)
-- If user says result was correct/wrong later
-- =========================================================
CREATE TABLE IF NOT EXISTS feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT,
    chat_log_id INTEGER,
    rating INTEGER CHECK (rating IN (1, 2, 3, 4, 5)),
    feedback_text TEXT,
    is_correct_prediction INTEGER, -- 1 yes, 0 no
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES user_sessions(session_id) ON DELETE SET NULL,
    FOREIGN KEY (chat_log_id) REFERENCES chat_logs(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_feedback_chat_log_id ON feedback(chat_log_id);

-- =========================================================
-- 9. OPTIONAL: GREETING LOGS
-- Track how users greet (useful for improving fuzzy greeting)
-- =========================================================
CREATE TABLE IF NOT EXISTS greeting_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT,
    user_input TEXT NOT NULL,
    detected_greeting_type TEXT, -- morning / afternoon / evening / night / hello / hi
    corrected_response TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES user_sessions(session_id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_greeting_logs_created_at ON greeting_logs(created_at);

-- =========================================================
-- 10. OPTIONAL SAMPLE DATA FOR TESTING
-- =========================================================
INSERT INTO diseases (
    plant_name, disease, symptom, detailed_symptoms,
    organic_treatment, chemical_treatment, prevention
)
SELECT
    'Rice',
    'Rice Blast',
    'Brown spots on leaves',
    'Diamond-shaped lesions with grey center and brown margins on leaves.',
    'Use neem oil spray and remove infected leaves.',
    'Apply tricyclazole or recommended fungicide.',
    'Use resistant varieties, balanced nitrogen, proper spacing.'
WHERE NOT EXISTS (
    SELECT 1 FROM diseases WHERE plant_name = 'Rice' AND disease = 'Rice Blast'
);

INSERT INTO diseases (
    plant_name, disease, symptom, detailed_symptoms,
    organic_treatment, chemical_treatment, prevention
)
SELECT
    'Wheat',
    'Stripe Rust',
    'Yellow stripes on leaves',
    'Long yellow-orange pustules arranged in stripes on leaves.',
    'Use compost tea and improve airflow.',
    'Apply propiconazole or suitable fungicide.',
    'Use resistant varieties and avoid excess irrigation.'
WHERE NOT EXISTS (
    SELECT 1 FROM diseases WHERE plant_name = 'Wheat' AND disease = 'Stripe Rust'
);

-- =========================================================
-- AGRICARE FINAL POSTGRESQL + PL/pgSQL FILE
-- Production-ready database for AgriCare Plant Disease Chatbot
-- =========================================================

-- =========================================================
-- 0. EXTENSIONS
-- =========================================================
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- =========================================================
-- 1. TABLE: diseases
-- Main plant disease knowledge base
-- =========================================================
CREATE TABLE IF NOT EXISTS diseases (
    id SERIAL PRIMARY KEY,
    plant_name VARCHAR(100) NOT NULL,
    disease_name VARCHAR(150) NOT NULL,
    symptom TEXT NOT NULL,
    detailed_symptoms TEXT,
    organic_treatment TEXT,
    chemical_treatment TEXT,
    prevention TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_diseases_plant_name ON diseases (plant_name);
CREATE INDEX IF NOT EXISTS idx_diseases_disease_name ON diseases (disease_name);
CREATE INDEX IF NOT EXISTS idx_diseases_plant_name_trgm ON diseases USING gin (LOWER(plant_name) gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_diseases_symptom_trgm ON diseases USING gin (LOWER(symptom) gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_diseases_detailed_symptoms_trgm ON diseases USING gin (LOWER(COALESCE(detailed_symptoms, '')) gin_trgm_ops);

-- =========================================================
-- 2. TABLE: plant_synonyms
-- Maps user-entered names like Paddy -> Rice, Corn -> Maize
-- =========================================================
CREATE TABLE IF NOT EXISTS plant_synonyms (
    id SERIAL PRIMARY KEY,
    synonym_name VARCHAR(100) NOT NULL UNIQUE,
    actual_plant_name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_plant_synonyms_synonym ON plant_synonyms (synonym_name);
CREATE INDEX IF NOT EXISTS idx_plant_synonyms_actual ON plant_synonyms (actual_plant_name);
CREATE INDEX IF NOT EXISTS idx_plant_synonyms_synonym_trgm ON plant_synonyms USING gin (LOWER(synonym_name) gin_trgm_ops);

-- =========================================================
-- 3. TABLE: chat_logs
-- Stores every text chat interaction
-- =========================================================
CREATE TABLE IF NOT EXISTS chat_logs (
    id BIGSERIAL PRIMARY KEY,
    session_id VARCHAR(255),
    user_message TEXT NOT NULL,
    cleaned_message TEXT,
    input_plant TEXT,
    input_symptom TEXT,
    resolved_plant_name TEXT,
    detected_disease TEXT,
    confidence_score NUMERIC(5,2),
    match_source TEXT,
    bot_response TEXT,
    is_casual BOOLEAN DEFAULT FALSE,
    response_type VARCHAR(50), -- greeting / disease / clarification / error / inappropriate
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_chat_logs_session_id ON chat_logs (session_id);
CREATE INDEX IF NOT EXISTS idx_chat_logs_created_at ON chat_logs (created_at);
CREATE INDEX IF NOT EXISTS idx_chat_logs_detected_disease ON chat_logs (detected_disease);

-- =========================================================
-- 4. TABLE: image_analysis_logs
-- Stores Plant.id image detection results
-- =========================================================
CREATE TABLE IF NOT EXISTS image_analysis_logs (
    id BIGSERIAL PRIMARY KEY,
    session_id VARCHAR(255),
    original_filename TEXT,
    file_size_bytes BIGINT,
    mime_type VARCHAR(100),
    detected_plant TEXT,
    detected_disease TEXT,
    is_healthy BOOLEAN,
    access_token TEXT,
    plant_id_status_code INTEGER,
    raw_api_response JSONB,
    bot_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_image_logs_session_id ON image_analysis_logs (session_id);
CREATE INDEX IF NOT EXISTS idx_image_logs_created_at ON image_analysis_logs (created_at);

-- =========================================================
-- 5. TABLE: error_logs
-- Stores backend errors and debugging data
-- =========================================================
CREATE TABLE IF NOT EXISTS error_logs (
    id BIGSERIAL PRIMARY KEY,
    session_id VARCHAR(255),
    endpoint TEXT,
    error_type TEXT,
    error_message TEXT,
    stack_trace TEXT,
    request_data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_error_logs_created_at ON error_logs (created_at);
CREATE INDEX IF NOT EXISTS idx_error_logs_endpoint ON error_logs (endpoint);

-- =========================================================
-- 6. TRIGGER FUNCTION: update updated_at automatically
-- =========================================================
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    NEW.updated_at := CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_set_updated_at_diseases ON diseases;

CREATE TRIGGER trg_set_updated_at_diseases
BEFORE UPDATE ON diseases
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

-- =========================================================
-- 7. FUNCTION: resolve_plant_name(input_plant)
-- Resolves direct match, synonym match, or fuzzy match
-- =========================================================
CREATE OR REPLACE FUNCTION resolve_plant_name(input_plant TEXT)
RETURNS TABLE (
    resolved_plant_name TEXT,
    plant_score NUMERIC,
    match_source TEXT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_input TEXT;
    v_direct_plant TEXT;
    v_synonym_plant TEXT;
    v_fuzzy_plant TEXT;
    v_fuzzy_score NUMERIC;
BEGIN
    v_input := LOWER(TRIM(input_plant));

    -- 1) Exact direct match in diseases
    SELECT DISTINCT d.plant_name
    INTO v_direct_plant
    FROM diseases d
    WHERE LOWER(d.plant_name) = v_input
    LIMIT 1;

    IF v_direct_plant IS NOT NULL THEN
        RETURN QUERY
        SELECT v_direct_plant::TEXT, 1.00::NUMERIC, 'direct_match'::TEXT;
        RETURN;
    END IF;

    -- 2) Exact synonym match
    SELECT ps.actual_plant_name
    INTO v_synonym_plant
    FROM plant_synonyms ps
    WHERE LOWER(ps.synonym_name) = v_input
    LIMIT 1;

    IF v_synonym_plant IS NOT NULL THEN
        RETURN QUERY
        SELECT v_synonym_plant::TEXT, 0.95::NUMERIC, 'synonym_match'::TEXT;
        RETURN;
    END IF;

    -- 3) Fuzzy match on diseases plant names
    SELECT p.plant_name, similarity(LOWER(p.plant_name), v_input)
    INTO v_fuzzy_plant, v_fuzzy_score
    FROM (
        SELECT DISTINCT plant_name FROM diseases
    ) p
    ORDER BY similarity(LOWER(p.plant_name), v_input) DESC
    LIMIT 1;

    IF v_fuzzy_score IS NOT NULL AND v_fuzzy_score >= 0.45 THEN
        RETURN QUERY
        SELECT v_fuzzy_plant::TEXT, v_fuzzy_score::NUMERIC, 'fuzzy_direct_match'::TEXT;
        RETURN;
    END IF;

    -- 4) Fuzzy match on synonym table
    SELECT ps.actual_plant_name, similarity(LOWER(ps.synonym_name), v_input)
    INTO v_fuzzy_plant, v_fuzzy_score
    FROM plant_synonyms ps
    ORDER BY similarity(LOWER(ps.synonym_name), v_input) DESC
    LIMIT 1;

    IF v_fuzzy_score IS NOT NULL AND v_fuzzy_score >= 0.40 THEN
        RETURN QUERY
        SELECT v_fuzzy_plant::TEXT, v_fuzzy_score::NUMERIC, 'fuzzy_synonym_match'::TEXT;
        RETURN;
    END IF;

    -- 5) No match
    RETURN QUERY
    SELECT NULL::TEXT, 0::NUMERIC, 'no_match'::TEXT;
END;
$$;

-- =========================================================
-- 8. FUNCTION: diagnose_plant_disease(input_plant, input_symptom)
-- Main production diagnosis function (recommended)
-- Resolves plant + fuzzy symptom matching
-- =========================================================
CREATE OR REPLACE FUNCTION diagnose_plant_disease(
    input_plant TEXT,
    input_symptom TEXT
)
RETURNS TABLE (
    resolved_plant_name TEXT,
    disease_name TEXT,
    symptom TEXT,
    detailed_symptoms TEXT,
    organic_treatment TEXT,
    chemical_treatment TEXT,
    prevention TEXT,
    plant_score NUMERIC,
    symptom_score NUMERIC,
    final_score NUMERIC,
    match_source TEXT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_resolved_plant TEXT;
    v_plant_score NUMERIC;
    v_match_source TEXT;
BEGIN
    -- Resolve plant name first
    SELECT r.resolved_plant_name, r.plant_score, r.match_source
    INTO v_resolved_plant, v_plant_score, v_match_source
    FROM resolve_plant_name(input_plant) r
    LIMIT 1;

    -- If no plant found
    IF v_resolved_plant IS NULL THEN
        RETURN QUERY
        SELECT
            NULL::TEXT,
            'Plant not found'::TEXT,
            NULL::TEXT,
            NULL::TEXT,
            NULL::TEXT,
            NULL::TEXT,
            'Please check the plant name or add a synonym.'::TEXT,
            0::NUMERIC,
            0::NUMERIC,
            0::NUMERIC,
            'no_match'::TEXT;
        RETURN;
    END IF;

    -- Return best disease for resolved plant using symptom fuzzy score
    RETURN QUERY
    WITH scored AS (
        SELECT
            d.plant_name::TEXT AS resolved_plant_name,
            d.disease_name::TEXT AS disease_name,
            d.symptom::TEXT AS symptom,
            d.detailed_symptoms::TEXT AS detailed_symptoms,
            d.organic_treatment::TEXT AS organic_treatment,
            d.chemical_treatment::TEXT AS chemical_treatment,
            d.prevention::TEXT AS prevention,
            v_plant_score::NUMERIC AS plant_score,
            GREATEST(
                similarity(LOWER(d.symptom), LOWER(COALESCE(input_symptom, ''))),
                similarity(LOWER(COALESCE(d.detailed_symptoms, '')), LOWER(COALESCE(input_symptom, '')))
            )::NUMERIC AS symptom_score,
            (
                (v_plant_score * 0.40) +
                (
                    GREATEST(
                        similarity(LOWER(d.symptom), LOWER(COALESCE(input_symptom, ''))),
                        similarity(LOWER(COALESCE(d.detailed_symptoms, '')), LOWER(COALESCE(input_symptom, '')))
                    ) * 0.60
                )
            )::NUMERIC AS final_score,
            v_match_source::TEXT AS match_source
        FROM diseases d
        WHERE LOWER(d.plant_name) = LOWER(v_resolved_plant)
    )
    SELECT
        s.resolved_plant_name,
        s.disease_name,
        s.symptom,
        s.detailed_symptoms,
        s.organic_treatment,
        s.chemical_treatment,
        s.prevention,
        ROUND(s.plant_score, 4),
        ROUND(s.symptom_score, 4),
        ROUND(s.final_score, 4),
        CASE
            WHEN s.symptom_score < 0.15 THEN 'plant_found_but_symptom_unclear'
            ELSE s.match_source
        END
    FROM scored s
    ORDER BY s.final_score DESC, s.symptom_score DESC
    LIMIT 1;
END;
$$;

-- =========================================================
-- 9. FUNCTION: get_top_2_disease_candidates(input_plant, input_symptom)
-- Useful when you want ambiguity handling like your Flask app
-- =========================================================
CREATE OR REPLACE FUNCTION get_top_2_disease_candidates(
    input_plant TEXT,
    input_symptom TEXT
)
RETURNS TABLE (
    rank_no INTEGER,
    resolved_plant_name TEXT,
    disease_name TEXT,
    symptom TEXT,
    detailed_symptoms TEXT,
    organic_treatment TEXT,
    chemical_treatment TEXT,
    prevention TEXT,
    plant_score NUMERIC,
    symptom_score NUMERIC,
    final_score NUMERIC,
    match_source TEXT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_resolved_plant TEXT;
    v_plant_score NUMERIC;
    v_match_source TEXT;
BEGIN
    -- Resolve plant first
    SELECT r.resolved_plant_name, r.plant_score, r.match_source
    INTO v_resolved_plant, v_plant_score, v_match_source
    FROM resolve_plant_name(input_plant) r
    LIMIT 1;

    IF v_resolved_plant IS NULL THEN
        RETURN QUERY
        SELECT
            1,
            NULL::TEXT,
            'Plant not found'::TEXT,
            NULL::TEXT,
            NULL::TEXT,
            NULL::TEXT,
            NULL::TEXT,
            'Please check plant name.'::TEXT,
            0::NUMERIC,
            0::NUMERIC,
            0::NUMERIC,
            'no_match'::TEXT;
        RETURN;
    END IF;

    RETURN QUERY
    WITH scored AS (
        SELECT
            d.plant_name::TEXT AS resolved_plant_name,
            d.disease_name::TEXT AS disease_name,
            d.symptom::TEXT AS symptom,
            d.detailed_symptoms::TEXT AS detailed_symptoms,
            d.organic_treatment::TEXT AS organic_treatment,
            d.chemical_treatment::TEXT AS chemical_treatment,
            d.prevention::TEXT AS prevention,
            v_plant_score::NUMERIC AS plant_score,
            GREATEST(
                similarity(LOWER(d.symptom), LOWER(COALESCE(input_symptom, ''))),
                similarity(LOWER(COALESCE(d.detailed_symptoms, '')), LOWER(COALESCE(input_symptom, '')))
            )::NUMERIC AS symptom_score,
            (
                (v_plant_score * 0.40) +
                (
                    GREATEST(
                        similarity(LOWER(d.symptom), LOWER(COALESCE(input_symptom, ''))),
                        similarity(LOWER(COALESCE(d.detailed_symptoms, '')), LOWER(COALESCE(input_symptom, '')))
                    ) * 0.60
                )
            )::NUMERIC AS final_score,
            v_match_source::TEXT AS match_source
        FROM diseases d
        WHERE LOWER(d.plant_name) = LOWER(v_resolved_plant)
    ),
    ranked AS (
        SELECT
            ROW_NUMBER() OVER (ORDER BY final_score DESC, symptom_score DESC) AS rank_no,
            *
        FROM scored
    )
    SELECT
        r.rank_no,
        r.resolved_plant_name,
        r.disease_name,
        r.symptom,
        r.detailed_symptoms,
        r.organic_treatment,
        r.chemical_treatment,
        r.prevention,
        ROUND(r.plant_score, 4),
        ROUND(r.symptom_score, 4),
        ROUND(r.final_score, 4),
        r.match_source
    FROM ranked r
    WHERE r.rank_no <= 2;
END;
$$;

-- =========================================================
-- 10. FUNCTION: log_chat_interaction(...)
-- Stores chatbot text interactions
-- =========================================================
CREATE OR REPLACE FUNCTION log_chat_interaction(
    p_session_id TEXT,
    p_user_message TEXT,
    p_cleaned_message TEXT,
    p_input_plant TEXT,
    p_input_symptom TEXT,
    p_resolved_plant_name TEXT,
    p_detected_disease TEXT,
    p_confidence_score NUMERIC,
    p_match_source TEXT,
    p_bot_response TEXT,
    p_is_casual BOOLEAN,
    p_response_type TEXT
)
RETURNS BIGINT
LANGUAGE plpgsql
AS $$
DECLARE
    v_id BIGINT;
BEGIN
    INSERT INTO chat_logs (
        session_id,
        user_message,
        cleaned_message,
        input_plant,
        input_symptom,
        resolved_plant_name,
        detected_disease,
        confidence_score,
        match_source,
        bot_response,
        is_casual,
        response_type
    )
    VALUES (
        p_session_id,
        p_user_message,
        p_cleaned_message,
        p_input_plant,
        p_input_symptom,
        p_resolved_plant_name,
        p_detected_disease,
        p_confidence_score,
        p_match_source,
        p_bot_response,
        p_is_casual,
        p_response_type
    )
    RETURNING id INTO v_id;

    RETURN v_id;
END;
$$;

-- =========================================================
-- 11. FUNCTION: log_image_analysis(...)
-- Stores Plant.id image results
-- =========================================================
CREATE OR REPLACE FUNCTION log_image_analysis(
    p_session_id TEXT,
    p_original_filename TEXT,
    p_file_size_bytes BIGINT,
    p_mime_type TEXT,
    p_detected_plant TEXT,
    p_detected_disease TEXT,
    p_is_healthy BOOLEAN,
    p_access_token TEXT,
    p_plant_id_status_code INTEGER,
    p_raw_api_response JSONB,
    p_bot_message TEXT
)
RETURNS BIGINT
LANGUAGE plpgsql
AS $$
DECLARE
    v_id BIGINT;
BEGIN
    INSERT INTO image_analysis_logs (
        session_id,
        original_filename,
        file_size_bytes,
        mime_type,
        detected_plant,
        detected_disease,
        is_healthy,
        access_token,
        plant_id_status_code,
        raw_api_response,
        bot_message
    )
    VALUES (
        p_session_id,
        p_original_filename,
        p_file_size_bytes,
        p_mime_type,
        p_detected_plant,
        p_detected_disease,
        p_is_healthy,
        p_access_token,
        p_plant_id_status_code,
        p_raw_api_response,
        p_bot_message
    )
    RETURNING id INTO v_id;

    RETURN v_id;
END;
$$;

-- =========================================================
-- 12. FUNCTION: log_error(...)
-- Stores backend errors
-- =========================================================
CREATE OR REPLACE FUNCTION log_error(
    p_session_id TEXT,
    p_endpoint TEXT,
    p_error_type TEXT,
    p_error_message TEXT,
    p_stack_trace TEXT,
    p_request_data JSONB
)
RETURNS BIGINT
LANGUAGE plpgsql
AS $$
DECLARE
    v_id BIGINT;
BEGIN
    INSERT INTO error_logs (
        session_id,
        endpoint,
        error_type,
        error_message,
        stack_trace,
        request_data
    )
    VALUES (
        p_session_id,
        p_endpoint,
        p_error_type,
        p_error_message,
        p_stack_trace,
        p_request_data
    )
    RETURNING id INTO v_id;

    RETURN v_id;
END;
$$;

-- =========================================================
-- 13. OPTIONAL VIEW: quick disease search dashboard
-- =========================================================
CREATE OR REPLACE VIEW v_disease_summary AS
SELECT
    plant_name,
    COUNT(*) AS disease_count
FROM diseases
GROUP BY plant_name
ORDER BY plant_name;

-- =========================================================
-- 14. SAMPLE DATA (safe inserts)
-- =========================================================

-- Rice
INSERT INTO diseases (
    plant_name, disease_name, symptom, detailed_symptoms,
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
    SELECT 1 FROM diseases
    WHERE plant_name = 'Rice' AND disease_name = 'Rice Blast'
);

INSERT INTO diseases (
    plant_name, disease_name, symptom, detailed_symptoms,
    organic_treatment, chemical_treatment, prevention
)
SELECT
    'Rice',
    'Bacterial Leaf Blight',
    'Yellowing and drying of leaf edges',
    'Water-soaked stripes near leaf tips that turn yellow and then dry.',
    'Remove infected leaves and use compost tea spray.',
    'Apply copper-based bactericide if recommended.',
    'Use resistant varieties, avoid excess nitrogen, proper drainage.'
WHERE NOT EXISTS (
    SELECT 1 FROM diseases
    WHERE plant_name = 'Rice' AND disease_name = 'Bacterial Leaf Blight'
);

-- Wheat
INSERT INTO diseases (
    plant_name, disease_name, symptom, detailed_symptoms,
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
    SELECT 1 FROM diseases
    WHERE plant_name = 'Wheat' AND disease_name = 'Stripe Rust'
);

-- Maize
INSERT INTO diseases (
    plant_name, disease_name, symptom, detailed_symptoms,
    organic_treatment, chemical_treatment, prevention
)
SELECT
    'Maize',
    'Leaf Blight',
    'Long brown lesions on leaves',
    'Elongated brown lesions that expand under humid conditions.',
    'Use bio-fungicides and improve drainage.',
    'Apply mancozeb or recommended fungicide.',
    'Use certified seeds and crop rotation.'
WHERE NOT EXISTS (
    SELECT 1 FROM diseases
    WHERE plant_name = 'Maize' AND disease_name = 'Leaf Blight'
);

-- Tomato
INSERT INTO diseases (
    plant_name, disease_name, symptom, detailed_symptoms,
    organic_treatment, chemical_treatment, prevention
)
SELECT
    'Tomato',
    'Early Blight',
    'Brown concentric spots on lower leaves',
    'Dark brown lesions with concentric rings, usually starting on older leaves.',
    'Remove affected leaves and spray neem-based fungicide.',
    'Apply chlorothalonil or mancozeb if advised.',
    'Crop rotation, avoid overhead watering, proper spacing.'
WHERE NOT EXISTS (
    SELECT 1 FROM diseases
    WHERE plant_name = 'Tomato' AND disease_name = 'Early Blight'
);

-- Synonyms
INSERT INTO plant_synonyms (synonym_name, actual_plant_name)
SELECT 'Paddy', 'Rice'
WHERE NOT EXISTS (SELECT 1 FROM plant_synonyms WHERE synonym_name = 'Paddy');

INSERT INTO plant_synonyms (synonym_name, actual_plant_name)
SELECT 'Dhaan', 'Rice'
WHERE NOT EXISTS (SELECT 1 FROM plant_synonyms WHERE synonym_name = 'Dhaan');

INSERT INTO plant_synonyms (synonym_name, actual_plant_name)
SELECT 'Corn', 'Maize'
WHERE NOT EXISTS (SELECT 1 FROM plant_synonyms WHERE synonym_name = 'Corn');

INSERT INTO plant_synonyms (synonym_name, actual_plant_name)
SELECT 'Makka', 'Maize'
WHERE NOT EXISTS (SELECT 1 FROM plant_synonyms WHERE synonym_name = 'Makka');

-- =========================================================
-- 15. EXAMPLE TEST QUERIES
-- Uncomment and run manually if needed
-- =========================================================
-- SELECT * FROM resolve_plant_name('Rice');
-- SELECT * FROM resolve_plant_name('Paddy');
-- SELECT * FROM resolve_plant_name('Pady');
-- SELECT * FROM diagnose_plant_disease('Rice', 'brown spots');
-- SELECT * FROM diagnose_plant_disease('Paddy', 'browm spots');
-- SELECT * FROM get_top_2_disease_candidates('Maize', 'brown lesions');

-- =========================================================
-- END OF FILE
-- =========================================================

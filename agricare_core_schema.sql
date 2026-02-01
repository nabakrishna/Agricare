CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE,
    farm_region VARCHAR(100),
    account_status VARCHAR(20) DEFAULT 'active',
    last_interaction_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE farm_assets (
    asset_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(user_id) ON DELETE CASCADE,
    crop_type VARCHAR(100),
    soil_composition JSONB,
    latitude DECIMAL(9,6),
    longitude DECIMAL(9,6),
    hectares_size DECIMAL(10,2)
);

CREATE TABLE query_logs (
    query_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(user_id),
    raw_user_query TEXT NOT NULL,
    ai_generated_result JSONB,
    category_tag VARCHAR(50),
    is_emergency BOOLEAN DEFAULT FALSE,
    response_time_ms INT,
    user_rating INT CHECK (user_rating BETWEEN 1 AND 5),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE system_events (
    event_id SERIAL PRIMARY KEY,
    severity VARCHAR(10),
    component_name VARCHAR(100),
    error_message TEXT,
    trace_id UUID,
    occured_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE FUNCTION refresh_user_heartbeat()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE users 
    SET last_interaction_at = NEW.created_at
    WHERE user_id = NEW.user_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_log_interaction
AFTER INSERT ON query_logs
FOR EACH ROW
EXECUTE FUNCTION refresh_user_heartbeat();

CREATE VIEW regional_issue_tracker AS
SELECT 
    u.farm_region,
    q.category_tag,
    COUNT(q.query_id) as total_occurrences,
    AVG(q.user_rating) as satisfaction_score
FROM query_logs q
JOIN users u ON q.user_id = u.user_id
WHERE q.created_at > NOW() - INTERVAL '7 days'
GROUP BY u.farm_region, q.category_tag;

CREATE INDEX idx_query_search ON query_logs USING GIN (ai_generated_result);
CREATE INDEX idx_user_region ON users(farm_region);
CREATE INDEX idx_geo_location ON farm_assets(latitude, longitude);

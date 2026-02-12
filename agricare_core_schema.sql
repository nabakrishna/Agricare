CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE,
   
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

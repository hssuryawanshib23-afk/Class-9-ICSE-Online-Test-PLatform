-- Additive only: new table used for login throttling. Safe to run against production;
-- the Streamlit app never reads or writes it.
CREATE TABLE IF NOT EXISTS login_attempts (
    id BIGSERIAL PRIMARY KEY,
    key TEXT NOT NULL,
    attempted_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_login_attempts_key_time ON login_attempts (key, attempted_at);

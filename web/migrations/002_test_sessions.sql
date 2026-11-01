-- Additive only: server-side state for tests in progress, so a refresh cannot reset the timer
-- and the correct answers never leave the server. The Streamlit app never reads or writes it.
CREATE TABLE IF NOT EXISTS test_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id INTEGER NOT NULL,
    kind TEXT NOT NULL CHECK (kind IN ('custom', 'admin')),
    admin_test_id INTEGER,
    questions JSONB NOT NULL,            -- [{ "id": 12, "options": ["C","A","D","B"] }, ...] in display order
    answers JSONB NOT NULL DEFAULT '{}', -- { "12": "A", ... } original option labels
    duration_seconds INTEGER NOT NULL,
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    submitted_at TIMESTAMPTZ,
    attempt_id INTEGER,
    score INTEGER,
    total INTEGER
);
CREATE INDEX IF NOT EXISTS idx_test_sessions_user ON test_sessions (user_id, started_at DESC);

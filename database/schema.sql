CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE IF NOT EXISTS users (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    email           VARCHAR(255) NOT NULL UNIQUE,
    password_hash   TEXT,                           -- NULL for OAuth users
    auth_provider   VARCHAR(50)  NOT NULL DEFAULT 'email',  
    full_name       VARCHAR(255),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS applications (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID        NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    company         VARCHAR(255) NOT NULL,
    role            VARCHAR(255) NOT NULL,
    status          VARCHAR(50)  NOT NULL DEFAULT 'applied',
                    CONSTRAINT valid_status CHECK (
                        status IN ('saved', 'applied', 'screening', 'interview', 'offer', 'rejected', 'withdrawn')
                    ),
    applied_date    DATE,
    source_url      TEXT,                           
    notes           TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


CREATE TABLE IF NOT EXISTS resumes (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID        NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    file_url        TEXT,                           -- Cloudinary/S3 URL
    file_name       VARCHAR(255),
    raw_text        TEXT,                           -- extracted by pdfminer/mammoth
    extracted_skills TEXT[]     NOT NULL DEFAULT '{}',  -- e.g. '{Python, Flask, SQL}'
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS analyses (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID        NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    resume_id       UUID        REFERENCES resumes(id) ON DELETE SET NULL,
    application_id  UUID        REFERENCES applications(id) ON DELETE SET NULL,  -- optional link
    jd_text         TEXT        NOT NULL,           -- raw job description pasted by user
    jd_role         VARCHAR(255),                   -- extracted by LangChain JD chain
    jd_company      VARCHAR(255),
    required_skills TEXT[]      NOT NULL DEFAULT '{}',
    matched_skills  TEXT[]      NOT NULL DEFAULT '{}',   -- in both resume & JD
    gap_skills      TEXT[]      NOT NULL DEFAULT '{}',   -- in JD, missing in resume
    match_score     FLOAT       CHECK (match_score BETWEEN 0.0 AND 1.0),
    suggestions     JSONB,      -- [{ "type": "add_skill", "text": "...", "priority": "high" }]
    raw_llm_output  JSONB,      -- full Gemini response for debugging
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS skill_trends (
    id              SERIAL      PRIMARY KEY,
    skill_name      VARCHAR(100) NOT NULL,
    frequency       INTEGER     NOT NULL DEFAULT 0,
    week_of         DATE        NOT NULL,           -- Monday of that week
    source_count    INTEGER     NOT NULL DEFAULT 0, -- total JDs analysed that week
    UNIQUE (skill_name, week_of)                    -- one row per skill per week
);

CREATE TABLE IF NOT EXISTS refresh_tokens (
    id              SERIAL      PRIMARY KEY,
    user_id         UUID        NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash      TEXT        NOT NULL UNIQUE,
    expires_at      TIMESTAMPTZ NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Applications: filter by user + status (Kanban board queries)
CREATE INDEX IF NOT EXISTS idx_applications_user_status
    ON applications(user_id, status);

-- Applications: sort by date
CREATE INDEX IF NOT EXISTS idx_applications_applied_date
    ON applications(user_id, applied_date DESC);

-- Resumes: latest per user
CREATE INDEX IF NOT EXISTS idx_resumes_user
    ON resumes(user_id, created_at DESC);

-- Analyses: latest per user
CREATE INDEX IF NOT EXISTS idx_analyses_user
    ON analyses(user_id, created_at DESC);

-- Skill trends: latest week lookups
CREATE INDEX IF NOT EXISTS idx_skill_trends_week
    ON skill_trends(week_of DESC, frequency DESC);

-- Refresh tokens: lookup by user
CREATE INDEX IF NOT EXISTS idx_refresh_tokens_user
    ON refresh_tokens(user_id);

--  AUTO-UPDATE updated_at  (via trigger)
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER trg_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE OR REPLACE TRIGGER trg_applications_updated_at
    BEFORE UPDATE ON applications
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

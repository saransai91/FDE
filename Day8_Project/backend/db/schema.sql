-- Employee Performance Review System — PostgreSQL schema (FROZEN)
-- 2 master tables + 1 transactional table.
-- Idempotent: drops and recreates the tables.

DROP TABLE IF EXISTS performance_reviews;
DROP TABLE IF EXISTS review_periods;
DROP TABLE IF EXISTS employees;

-- Master: employees must exist before they can be reviewed.
CREATE TABLE employees (
    employee_id  VARCHAR(20)  PRIMARY KEY,                       -- e.g. EMP101 (PK => unique, NOT NULL)
    name         VARCHAR(100) NOT NULL,
    department   VARCHAR(100) NOT NULL,
    designation  VARCHAR(100) NOT NULL,
    email        VARCHAR(150) NOT NULL UNIQUE,
    status       VARCHAR(20)  NOT NULL DEFAULT 'Active'
                 CHECK (status IN ('Active', 'Inactive'))
);

-- Master: feeds the review period dropdown.
CREATE TABLE review_periods (
    review_period_id  SERIAL      PRIMARY KEY,
    name              VARCHAR(50) NOT NULL UNIQUE,               -- e.g. Q1 2026, H1 2026, FY 2026
    period_type       VARCHAR(20) NOT NULL
                      CHECK (period_type IN ('Monthly', 'Quarterly', 'Half-Yearly', 'Annual')),
    start_date        DATE        NOT NULL,
    end_date          DATE        NOT NULL,
    status            VARCHAR(10) NOT NULL DEFAULT 'Open'
                      CHECK (status IN ('Open', 'Closed')),
    CONSTRAINT chk_period_dates CHECK (end_date >= start_date)
);

-- Transactional: one review per employee per review period.
CREATE TABLE performance_reviews (
    review_id         SERIAL       PRIMARY KEY,
    employee_id       VARCHAR(20)  NOT NULL REFERENCES employees(employee_id)           ON DELETE RESTRICT,
    review_period_id  INTEGER      NOT NULL REFERENCES review_periods(review_period_id) ON DELETE RESTRICT,
    quality_rating    SMALLINT     NOT NULL CHECK (quality_rating  BETWEEN 1 AND 5),
    delivery_rating   SMALLINT     NOT NULL CHECK (delivery_rating BETWEEN 1 AND 5),
    teamwork_rating   SMALLINT     NOT NULL CHECK (teamwork_rating BETWEEN 1 AND 5),
    average_rating    NUMERIC(3,2) NOT NULL CHECK (average_rating  BETWEEN 1 AND 5),  -- (q + d + t) / 3
    comments          TEXT         NOT NULL CHECK (length(btrim(comments)) BETWEEN 1 AND 2000),
    created_at        TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_review_employee_period UNIQUE (employee_id, review_period_id)
);

CREATE INDEX ix_reviews_period   ON performance_reviews(review_period_id);
CREATE INDEX ix_reviews_employee ON performance_reviews(employee_id);

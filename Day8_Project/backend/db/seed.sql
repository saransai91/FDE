-- Seed data: 12 employees, 7 review periods, 12 sample reviews. Run after schema.sql.
-- All periods are Open so everything can be tested (requirement: "treat all as open for testing").

INSERT INTO employees (employee_id, name, department, designation, email, status) VALUES
('EMP101', 'John Smith',        'Engineering', 'Senior Developer',   'john.smith@example.com',        'Active'),
('EMP102', 'Sarah Johnson',     'Engineering', 'Developer',          'sarah.johnson@example.com',     'Active'),
('EMP103', 'Michael Lee',       'QA',          'QA Lead',            'michael.lee@example.com',       'Active'),
('EMP104', 'Priya Sharma',      'QA',          'QA Engineer',        'priya.sharma@example.com',      'Active'),
('EMP105', 'David Brown',       'Product',     'Product Manager',    'david.brown@example.com',       'Active'),
('EMP106', 'Anitha Raman',      'Engineering', 'Tech Lead',          'anitha.raman@example.com',      'Active'),
('EMP107', 'Robert Wilson',     'Finance',     'Analyst',            'robert.wilson@example.com',     'Active'),
('EMP108', 'Lakshmi Iyer',      'HR',          'HR Partner',         'lakshmi.iyer@example.com',      'Active'),
('EMP109', 'James Taylor',      'Sales',       'Account Executive',  'james.taylor@example.com',      'Active'),
('EMP110', 'Karthik Subramani', 'Engineering', 'Developer',          'karthik.subramani@example.com', 'Active'),
('EMP111', 'Emily Davis',       'Product',     'Product Owner',      'emily.davis@example.com',       'Active'),
('EMP112', 'Arjun Mehta',       'QA',          'Automation Engineer','arjun.mehta@example.com',       'Active');

INSERT INTO review_periods (name, period_type, start_date, end_date, status) VALUES
('FY 2025', 'Annual',      '2025-01-01', '2025-12-31', 'Open'),
('H1 2026', 'Half-Yearly', '2026-01-01', '2026-06-30', 'Open'),
('H2 2026', 'Half-Yearly', '2026-07-01', '2026-12-31', 'Open'),
('Q1 2026', 'Quarterly',   '2026-01-01', '2026-03-31', 'Open'),
('Q2 2026', 'Quarterly',   '2026-04-01', '2026-06-30', 'Open'),
('Q3 2026', 'Quarterly',   '2026-07-01', '2026-09-30', 'Open'),
('Q4 2026', 'Quarterly',   '2026-10-01', '2026-12-31', 'Open');

-- average_rating is computed the same way as the service: ROUND((q + d + t) / 3, 2)
INSERT INTO performance_reviews
    (employee_id, review_period_id, quality_rating, delivery_rating, teamwork_rating, average_rating, comments, created_at)
SELECT r.emp, p.review_period_id, r.q, r.d, r.t, ROUND((r.q + r.d + r.t) / 3.0, 2), r.comments, r.created_at::timestamptz
FROM (VALUES
    ('EMP101', 'FY 2025', 4, 4, 4, 'Consistent and dependable across the year.',        '2026-01-10 10:30:00+00'),
    ('EMP101', 'H1 2026', 4, 5, 4, 'Strong performer with great teamwork.',             '2026-07-10 10:30:00+00'),
    ('EMP101', 'Q3 2026', 5, 5, 4, 'Led the sprint demo and unblocked the team.',       '2026-10-05 09:00:00+00'),
    ('EMP102', 'H1 2026', 3, 4, 4, 'Reliable delivery; can improve code quality.',       '2026-07-11 09:15:00+00'),
    ('EMP103', 'H1 2026', 5, 5, 5, 'Outstanding quality across all releases.',           '2026-07-12 14:00:00+00'),
    ('EMP104', 'H1 2026', 2, 3, 3, 'Needs to focus on ownership of test cycles.',        '2026-07-13 11:45:00+00'),
    ('EMP105', 'H1 2026', 4, 4, 5, 'Excellent collaboration with engineering.',           '2026-07-14 16:20:00+00'),
    ('EMP106', 'H1 2026', 4, 3, 4, 'Good technical skills; deadlines slipped twice.',    '2026-07-15 10:00:00+00'),
    ('EMP107', 'Q2 2026', 5, 4, 4, 'Accurate and timely financial reporting.',           '2026-07-16 13:10:00+00'),
    ('EMP108', 'Q2 2026', 3, 3, 5, 'Great people skills; improve process docs.',         '2026-07-17 09:40:00+00'),
    ('EMP109', 'FY 2025', 3, 4, 3, 'Met sales targets for the year.',                    '2026-01-13 10:30:00+00'),
    ('EMP110', 'Q3 2026', 4, 5, 4, 'Delivered the payments module ahead of schedule.',  '2026-10-08 10:30:00+00')
) AS r(emp, period_name, q, d, t, comments, created_at)
JOIN review_periods p ON p.name = r.period_name;

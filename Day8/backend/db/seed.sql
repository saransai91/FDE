-- Seed data for local testing: 25 employees, 7 review periods, 15 sample reviews.
-- Run after schema.sql.

INSERT INTO employees (employee_id, name, department, email, status) VALUES
('EMP101', 'John Smith',        'Engineering', 'john.smith@testleaf.com',        'Active'),
('EMP102', 'Sarah Johnson',     'Engineering', 'sarah.johnson@testleaf.com',     'Active'),
('EMP103', 'Michael Lee',       'QA',          'michael.lee@testleaf.com',       'Active'),
('EMP104', 'Priya Sharma',      'QA',          'priya.sharma@testleaf.com',      'Active'),
('EMP105', 'David Brown',       'Product',     'david.brown@testleaf.com',       'Active'),
('EMP106', 'Anitha Raman',      'Engineering', 'anitha.raman@testleaf.com',      'Active'),
('EMP107', 'Robert Wilson',     'Finance',     'robert.wilson@testleaf.com',     'Active'),
('EMP108', 'Lakshmi Iyer',      'HR',          'lakshmi.iyer@testleaf.com',      'Active'),
('EMP109', 'James Taylor',      'Sales',       'james.taylor@testleaf.com',      'Active'),
('EMP110', 'Karthik Subramani', 'Engineering', 'karthik.subramani@testleaf.com', 'Active'),
('EMP111', 'Emily Davis',       'Product',     'emily.davis@testleaf.com',       'Active'),
('EMP112', 'Arjun Mehta',       'QA',          'arjun.mehta@testleaf.com',       'Active'),
('EMP113', 'Olivia Martinez',   'Sales',       'olivia.martinez@testleaf.com',   'Active'),
('EMP114', 'Deepa Krishnan',    'Finance',     'deepa.krishnan@testleaf.com',    'Active'),
('EMP115', 'William Anderson',  'Engineering', 'william.anderson@testleaf.com',  'Active'),
('EMP116', 'Meena Pillai',      'HR',          'meena.pillai@testleaf.com',      'Active'),
('EMP117', 'Daniel Thomas',     'QA',          'daniel.thomas@testleaf.com',     'Active'),
('EMP118', 'Divya Nair',        'Product',     'divya.nair@testleaf.com',        'Active'),
('EMP119', 'Christopher Moore', 'Sales',       'christopher.moore@testleaf.com', 'Active'),
('EMP120', 'Sanjay Gupta',      'Engineering', 'sanjay.gupta@testleaf.com',      'Active'),
('EMP121', 'Jessica White',     'Finance',     'jessica.white@testleaf.com',     'Active'),
('EMP122', 'Vikram Reddy',      'QA',          'vikram.reddy@testleaf.com',      'Active'),
('EMP123', 'Sophia Harris',     'HR',          'sophia.harris@testleaf.com',     'Active'),
('EMP124', 'Ravi Kumar',        'Engineering', 'ravi.kumar@testleaf.com',        'Inactive'),
('EMP125', 'Laura Clark',       'Sales',       'laura.clark@testleaf.com',       'Inactive');

INSERT INTO review_periods (name, start_date, end_date, status) VALUES
('H1 2024', '2024-01-01', '2024-06-30', 'Closed'),
('H2 2024', '2024-07-01', '2024-12-31', 'Closed'),
('H1 2025', '2025-01-01', '2025-06-30', 'Closed'),
('H2 2025', '2025-07-01', '2025-12-31', 'Closed'),
('FY 2025', '2025-01-01', '2025-12-31', 'Closed'),
('H1 2026', '2026-01-01', '2026-06-30', 'Open'),
('H2 2026', '2026-07-01', '2026-12-31', 'Open');

-- Sample reviews. average_rating is computed the same way the service does (BR-2).
INSERT INTO performance_reviews
    (employee_id, period_id, quality_rating, delivery_rating, teamwork_rating, average_rating, comments, created_at)
SELECT e.id, p.id, r.q, r.d, r.t, ROUND((r.q + r.d + r.t) / 3.0, 2), r.comments, r.created_at::timestamp
FROM (VALUES
    ('EMP101', 'H1 2026', 4, 5, 4, 'Strong performer with great teamwork.',            '2026-07-10 10:30:00'),
    ('EMP102', 'H1 2026', 3, 4, 4, 'Reliable delivery; can improve code quality.',      '2026-07-11 09:15:00'),
    ('EMP103', 'H1 2026', 5, 5, 5, 'Outstanding quality across all releases.',          '2026-07-12 14:00:00'),
    ('EMP104', 'H1 2026', 2, 3, 3, 'Needs to focus on ownership of test cycles.',       '2026-07-13 11:45:00'),
    ('EMP105', 'H1 2026', 4, 4, 5, 'Excellent collaboration with engineering.',          '2026-07-14 16:20:00'),
    ('EMP106', 'H1 2026', 4, 3, 4, 'Good technical skills, deadlines slipped twice.',   '2026-07-15 10:00:00'),
    ('EMP107', 'H1 2026', 5, 4, 4, 'Accurate and timely financial reporting.',          '2026-07-16 13:10:00'),
    ('EMP108', 'H1 2026', 3, 3, 5, 'Great people skills; improve process docs.',        '2026-07-17 09:40:00'),
    ('EMP101', 'H2 2025', 4, 4, 4, 'Consistent and dependable.',                       '2026-01-10 10:30:00'),
    ('EMP102', 'H2 2025', 4, 3, 3, 'Solid work, more proactive communication needed.', '2026-01-11 10:30:00'),
    ('EMP103', 'H2 2025', 5, 4, 5, 'Led the regression automation effort.',            '2026-01-12 10:30:00'),
    ('EMP109', 'H2 2025', 3, 4, 3, 'Met sales targets for the half.',                   '2026-01-13 10:30:00'),
    ('EMP110', 'H1 2025', 4, 5, 4, 'Delivered the payments module ahead of schedule.', '2025-07-08 10:30:00'),
    ('EMP111', 'H1 2025', 3, 3, 4, 'Good roadmap ownership.',                           '2025-07-09 10:30:00'),
    ('EMP124', 'H2 2024', 3, 2, 3, 'Review recorded before the employee left.',        '2025-01-09 10:30:00')
) AS r(emp_code, period_name, q, d, t, comments, created_at)
JOIN employees      e ON e.employee_id = r.emp_code
JOIN review_periods p ON p.name        = r.period_name;

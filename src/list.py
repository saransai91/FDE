employees = [
    [101, "Ramesh", 200000],
    [102, "Saranya", 240000],
    [103, "Alexander", 300000],
    [104, "Priyanka", 220000],
    [105, "Raj", 150000]
]

for employee in employees:
    employee_id = employee[0]
    name = employee[1]
    salary = employee[2]

    if len(name) > 6 and salary < 250000:
        print(name)
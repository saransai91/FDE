employees = [
    {"id": 101, "name": "Ramesh", "salary": 200000},
    {"id": 102, "name": "Saranya", "salary": 240000},
    {"id": 103, "name": "Alexander", "salary": 300000},
    {"id": 104, "name": "Priyanka", "salary": 220000},
    {"id": 105, "name": "Raj", "salary": 150000}
]

for employee in employees:
    if len(employee["name"]) > 6 and employee["salary"] < 250000:
        print(employee["name"])
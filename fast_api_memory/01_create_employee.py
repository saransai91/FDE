from fastapi import APIRouter

router = APIRouter()

employees = []

@router.post("/employees")
def create_employee(employee: dict):
    employees.append(employee)
    return {
        "message": "Employee created successfully",
        "employee": employee
    }
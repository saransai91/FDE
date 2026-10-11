
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field, ConfigDict

app = FastAPI(title="Payments API")


class Payment(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    invoice_id: str = Field(min_length=1)
    paid: float = Field(ge=0)


class PaymentResponse(Payment):
    payment_id: int


payments = [
    {"payment_id": 1, "invoice_id": "INV-101", "paid": 85000},
    {"payment_id": 2, "invoice_id": "INV-101", "paid": 85000},
    {"payment_id": 3, "invoice_id": "INV-104", "paid": 60000},
    {"payment_id": 4, "invoice_id": "INV-109", "paid": 12000},
]


# GET: Retrieve all payments
@app.get("/payments", response_model=list[PaymentResponse])
def get_payments():
    return payments


# GET: Retrieve one payment by payment ID
@app.get("/payments/{payment_id}", response_model=PaymentResponse)
def get_payment(payment_id: int):
    for payment in payments:
        if payment["payment_id"] == payment_id:
            return payment

    raise HTTPException(
        status_code=404,
        detail="Payment not found"
    )


# POST: Create a payment
@app.post(
    "/payments",
    response_model=PaymentResponse,
    status_code=status.HTTP_201_CREATED
)
def create_payment(payment: Payment):
    new_id = max(
        (p["payment_id"] for p in payments),
        default=0
    ) + 1

    new_payment = {
        "payment_id": new_id,
        **payment.model_dump()
    }

    payments.append(new_payment)
    return new_payment


# PUT: Update an existing payment
@app.put("/payments/{payment_id}", response_model=PaymentResponse)
def update_payment(payment_id: int, updated: Payment):
    for index, payment in enumerate(payments):
        if payment["payment_id"] == payment_id:
            payments[index] = {
                "payment_id": payment_id,
                **updated.model_dump()
            }
            return payments[index]

    raise HTTPException(
        status_code=404,
        detail="Payment not found"
    )


# DELETE: Delete a payment
@app.delete("/payments/{payment_id}")
def delete_payment(payment_id: int):
    for index, payment in enumerate(payments):
        if payment["payment_id"] == payment_id:
            deleted = payments.pop(index)
            return {
                "message": "Payment deleted successfully",
                "payment": deleted
            }

    raise HTTPException(
        status_code=404,
        detail="Payment not found"
    )

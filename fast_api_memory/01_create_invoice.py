from fastapi import APIRouter
from fast_api_memory.data_store import invoices
from fast_api_memory.models import Invoice

router = APIRouter()


@router.post("/invoices")
def create_invoice(invoice: Invoice):

    invoices.append(invoice.model_dump())

    return {
        "message": "Invoice created successfully",
        "invoice": invoice
    }
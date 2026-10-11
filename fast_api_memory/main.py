import importlib
from fastapi import FastAPI

create_invoice = importlib.import_module("fast_api_memory.01_create_invoice").router
get_invoices = importlib.import_module("fast_api_memory.01_get_invoices").router

app = FastAPI()

app.include_router(create_invoice)
app.include_router(get_invoices)
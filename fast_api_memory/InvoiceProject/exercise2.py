
import json

DATA_FILE = "data/invoices.json"

with open(DATA_FILE, "r") as f:
    invoices = json.load(f)

seen = set()
duplicates = []

for invoice in invoices:
    invoice_id = invoice["invoice_id"]

    if invoice_id in seen:
        duplicates.append(invoice)
    else:
        seen.add(invoice_id)

print("Duplicate invoices:")

for invoice in duplicates:
    print(invoice)
